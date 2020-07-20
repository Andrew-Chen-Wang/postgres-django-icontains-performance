import os
import operator
import timeit

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from public.models import Item, ItemWithoutIndex


def load_words() -> set:
    """370099 words in the set"""
    with open("words_alpha.txt") as file:
        valid_words = set(file.read().split())
    return valid_words


words = [x.lower() for x in load_words()]


def find_most_frequent_letter_combo(length: int, start: int, end: int) -> str:
    """https://www.reddit.com/r/learnpython/comments/3o930t/finding_pairs_of_letter_frequency_in_python/"""
    pairs: dict = {}
    for word in words[start:end]:
        # treat the word as a sequence, skip the last "length" letters
        for index, letter in enumerate(word[:-length]):
            # form a pair with its next letter
            pair = letter
            for x in range(length - 1):
                pair += word[index + x + 1]
            # count the pair in the dict by adding 1 to the current value
            # setdefault will return 0 if the pair is not yet in the dict
            pairs[pair] = pairs.setdefault(pair, 0) + 1
    return max(pairs.items(), key=operator.itemgetter(1))[0]


def timing(string, queryset):
    start = timeit.default_timer()
    query_explain = queryset.explain()
    stop = timeit.default_timer()
    print(string, f"Time: {stop - start}\n", query_explain)


def benchmark(start: int, end: int, pretty: bool):
    # Testing short length - 2 chars - and long - 4 chars.
    if start == 0:
        start = 1
    freq_2_combo = find_most_frequent_letter_combo(2, start - 1, end - 1)
    freq_4_combo = find_most_frequent_letter_combo(4, start - 1, end - 1)
    for x in [freq_2_combo, freq_4_combo]:
        print(f"Length: {len(x)}")
        timing("CharField, no Index:\n", Item.objects.filter(name__icontains=x)[:15])
        timing("CharField, w/ Index:\n", ItemWithoutIndex.objects.filter(name__icontains=x)[:15])
        timing("SearchVectorField, no Index:\n", Item.objects.filter(name_search__icontains=x)[:15])
        timing("SearchVectorField, w/ Index:\n", ItemWithoutIndex.objects.filter(name_search__icontains=x)[:15])


def create_items(wanted_count: int):
    current_count = Item.objects.count()
    appending_count = wanted_count - current_count
    if appending_count > 0:
        print(f"Creating {appending_count} more items for {wanted_count} total.")
        items = []
        itemsWOIndex = []
        for i, char in enumerate(words):
            if i < current_count:
                continue
            elif i == wanted_count:
                break
            items.append(Item(name=char))
            itemsWOIndex.append(ItemWithoutIndex(name=char))
        Item.objects.bulk_create(items, batch_size=5000)
        ItemWithoutIndex.objects.bulk_create(itemsWOIndex, batch_size=5000)

    assert Item.objects.count() == wanted_count, f"{Item.objects.count()} {wanted_count}"

    # Calibrate index
    list(Item.objects.all())


class Command(BaseCommand):
    help = (
        "Generates test data items and benchmarks"
        "which searches faster at different record numbers."
        "For consistency purposes, we will limit results to 15."
    )
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument('-l', "--less", type=bool, help='Show more or less detail.', default=False)
        parser.add_argument('-n', type=int, help='The level/arbitrary num of objects to create.')
        parser.add_argument('--use-existing', type=bool, help="Specify if use existing database", default=False)

    def handle(self, *args, **options):
        if not options["use_existing"]:
            call_command("flush", "--noinput")

        # Check if words_alpha.txt exists
        path_to_dictionary = os.path.join(settings.BASE_DIR, "words_alpha.txt")
        if not os.path.exists(path_to_dictionary):
            import zipfile
            try:
                with zipfile.ZipFile(path_to_dictionary[:-3] + "zip", "r") as zip_ref:
                    zip_ref.extractall(settings.BASE_DIR)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"You must include the zip file of the English"
                                        f" dictionary in the BASE_DIR, specified:\n{e}.")

        # Start Tests
        # Level 1: first 20,000 items
        create_items(20000)
        if options["n"] in (1, None):
            print("Level 1: first 20,000 items")
            benchmark(0, 20000, options["less"])

        # Level 2: + 80,000 = 100,000 items
        create_items(100000)
        if options["n"] in (2, None):
            print("Level 2: + 80,000 = 100,000 items")
            benchmark(20000, 100000, options["less"])

        # Level 3: + 100,000 = 200,000 items
        create_items(200000)
        if options["n"] in (3, None):
            print("Level 3: + 100,000 = 200,000 items")
            benchmark(100000, 200000, options["less"])

        # Level 4: + 170,099 = 370,099 items, all words
        create_items(370099)
        if options["n"] in (4, None):
            print("Level 4: + 170,099 = 370099 items, all words")
            benchmark(200000, 370099, options["less"])

        # Level 5: + 300,000 = 500,000 items
        # create_items(500000)
        # # This will be kind of weird in that we're combining words
        # # from opposite ends of the alphabet and scrambling them.
        # if options["n"] in (5, None):
        #     print("Level 5: + 300,000 = 500,000 items")
        #     benchmark(370099, 500000, options["less"])
