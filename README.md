# Typeahead Django and Postgres FTS using icontains

By: [Andrew Chen Wang](https://github.com/Andrew-Chen-Wang)

Created on July 19, 2020

The purpose of this library is to see which 
field type works better with `icontains`: `CharField(max_length=100)`
or a __constantly__ updated `SearchVectorField(null=True)`.

This library is dedicated to [Donate Anything](https://github.com/Donate-Anything/Donate-Anything)
which is for searching items or things to donate, returning
results of organizations or services that can fulfill your donations.

## Benchmarks

I'm using Postgres 12.3 and Django 3.08 on a MacBook Air.

I tested this by using a dictionary of English words. There are
370099 words used. I filtered using `icontains` on each table
with 2 or 4 characters. The X axis is the number of items in
the table. The index used was GIN; specifics are in
`public/models.py`. Consistency was kept by having a `LIMIT 15`
to make sure latency wasn't a factor.

Filtering was based on the most frequent two or four letter combo.
I also added the index size (note, they're the same regardless of
the table.). Each query was performed 10,000 times to find an average.

The following are the results for a two letter query using `icontains`.

|                      | 20,000                 | 100,000                | 200,000                | 370,099              |
|----------------------|------------------------|------------------------|------------------------|----------------------|
| CharField            | 4.0563607999998475e-06 | 1.0140782000068073e-06 | 3.345731800025931e-06  | 1.1925746000031268e-06  |
| SearchVectorField    | 4.478697200006998e-06  | 5.1264475000078136e-06 | 6.7940737999805374e-06 | 1.1600425299964457e-05 |
| Char + Index         | 1.3099410999975802e-06 | 1.2240283000011232e-06 | 1.1483104000618028e-06 | 1.1056564999449848e-06  |
| SearchVector + Index | 1.0438225999999772e-06 | 1.256916100008354e-06  | 1.0608623999516453e-06 | 2.409129799882237e-06 |
| BTree Index (bytes)  | 696320                 | 4210688                | 8265728                | 14548992             |
| GIN Index (bytes)    | 499712                 | 2433024                | 11460608               | 12640256             |

The following are the results for a four letter query using `icontains`.

|                      | 20,000                 | 100,000                | 200,000                | 370,099                |
|----------------------|------------------------|------------------------|------------------------|------------------------|
| CharField            | 1.5397245999964504e-06 | 1.127325100011589e-06  | 1.0684846000060589e-06 | 2.4510758000459986e-06 |
| SearchVectorField    | 2.8315995000024687e-06 | 2.4477684000036247e-06 | 6.202969099967959e-06  | 1.1837768399951188e-05 |
| Char + Index         | 2.0083184000008637e-06 | 1.2677050000007739e-06 | 1.0630535000139218e-06 | 1.0793565999776433e-06 |
| SearchVector + Index | 1.5768463000013888e-06 | 1.6528725999929605e-06 | 1.6786233000360084e-06 | 1.7016839999612899e-06 |
| BTree Index (bytes)  | 696320                 | 4210688                | 8265728                | 14426112               |
| GIN Index (bytes)    | 499712                 | 2433024                | 11460608               | 15204352               |

Edit: Note the results were slightly incorrect since the evaluation of the queryset
didn't actually execute... because I was really tired and forgot `.explain()` won't
actually perform the query. Using Postgres's ANALYZE flag will execute it, but the
printing actually takes a little more time in the performance. The actual numbers
are in results.txt and have also been updated here. Opinion remains the same.

After multiple experiments, the B-Tree index size stays relatively the same, GIN too except for the first 100 thousand.

To see the full results, check out [results.txt](https://github.com/Andrew-Chen-Wang/postgres-django-icontains-performance/blob/master/results.txt).

## Conclusion

~~The two biggest factors seemed to be the length of user input
and the number of objects in the database.~~ Scratch that,
there's VERY NEGLIGIBLE difference for performing single word
queries. 

This is mainly for finding the most efficient method of querying
using `icontains`. For Donate Anything, there probably won't
be more than a million items; however, there will be lots of
translations. I plan on adding some plug-ins like stem removing
and the un-accent extension to save some space in addition to
a dictionary of words that definitely shouldn't be in the tokenization.

Basically, there's no need for the SearchVectorField. A simple
CharField is enough, and although
it seems like there's almost no need for the B-Tree index,
we do have to make sure there is uniqueness for the name.

Based on the results, the search time is minuscule, even up to
370099 words. This is regardless of the field and index. 
~~A caveat is definitely the fact that many items
are two or more words long.~~

## Usage

I assume you have Postgres installed with a superuser Postgres. You
can update the database settings in `typeahead_django/settings.py`.

1. Install the dependencies. `pip install -r requirements.txt`
2. Run `python manage.py benchmark`

This command will run the full test suite. For less details,
specify the "--less" flag.

For more refined testing, you can specify the number of objects in
your dataset with the "-n" flag. This acts as a game "level" (first is 1).
**Please do not remove or add records to the database as the command
relies on the set number of objects to properly run the tests.**
For example, the word "chair" might be in the first 20,000 records.
If you delete it, you screwed over test 1.

## License and Credit

This is licensed under Apache 2.0. You can view the license in the LICENSE file.

The dataset used is a dictionary of words by infochimps and re-made by dwyl.
You can find this information here: https://github.com/dwyl/english-words