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
the table.)

The following are the results for a two letter query using `icontains`.

|                      | 20,000               | 100,000              | 200,000              | 370,099              |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .0018870119999991886 | .0011454019999987963 | .0007141570000044339 | .000861889999995924  |
| SearchVectorField    | .0008137989999994488 | .0006560049999997375 | .0007020010000005072 | .0006000810000017509 |
| Char + Index         | .0006321439999998901 | .0008057759999999803 | .0005880140000016354 | .000538313999996376  |
| SearchVector + Index | .0005834329999991894 | .0009325770000003786 | .0005893750000041109 | .0005222089999961099 |
| BTree Index (bytes)  | 770048               | 4055040              | 7970816              | 14606336             |
| GIN Index (bytes)    | 499712               | 2433024              | 11370496             | 15851520             |

The following are the results for a four letter query using `icontains`.

|                      | 20,000               | 100,000              | 200,000              | 370,099              |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .0005825000000001523 | .0013767680000000837 | .0005893750000041109 | .0005648419999957355 |
| SearchVectorField    | .0005575970000002428 | .0008295879999984379 | .0007504889999978559 | .0005678309999979092 |
| Char + Index         | .0005883070000001211 | .0007131819999983691 | .001916348000001733  | .0006092080000001943 |
| SearchVector + Index | .0005402690000000376 | .0006276289999966878 | .0006567059999937896 | .0005303149999988932 |
| BTree Index (bytes)  | 770048               | 4055040              | 7970816              | 14606336             |
| GIN Index (bytes)    | 499712               | 2433024              | 11370496             | 15851520             |

To see the full results, check out [results.txt](https://github.com/Andrew-Chen-Wang/postgres-django-icontains-performance/blob/master/results.txt).

## Conclusion

The two biggest factors seemed to be the length of user input
and the number of objects in the database. There is
also a slight inverse relationship between the two.

This is mainly for finding the most efficient method of querying
using `icontains`. For Donate Anything, there probably won't
be more than a million items; however, there will be lots of
translations. I plan on adding some plug-ins like stem removing
and the un-accent extension to save some space in addition to
a dictionary of words that definitely shouldn't be in the tokenization.

Based on the results, the search time is minimal, even up to
370099 words. This is regardless of the field and index. 
A caveat is definitely the fact that many items
are two or more words long.

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