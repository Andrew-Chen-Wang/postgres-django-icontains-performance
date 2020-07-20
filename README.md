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

The following are the results for a two letter query using `icontains`.

|                      | 20,000               | 100,000              | 200,000              | 370099               |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .014103893999999784  | .0009496909999988645 | .0008854089999985604 | .007795620000003112  |
| SearchVectorField    | .0009419720000005682 | .0004928250000002521 | .0005886239999988163 | .0005851559999996425 |
| Char + Index         | .0012791679999999417 | .0006036560000008961 | .0005743679999987705 | .0008722190000014507 |
| SearchVector + Index | .0008850980000003617 | .0005101700000000875 | .0008045750000000851 | .000564265000001285  |

The following are the results for a four letter query using `icontains`.

|                      | 20,000               | 100,000              | 200,000              | 370099               |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .0008273679999994954 | .000500467000000171  | .0007317950000000906 | .0005774899999977379 |
| SearchVectorField    | .000646103000000231  | .0005348899999990664 | .0013678130000016608 | .0005922900000001619 |
| Char + Index         | .000635790000000469  | .0004974549999996469 | .02593128100000186   | .0005812670000011622 |
| SearchVector + Index | .0006452390000006858 | .0004988819999987015 | .0012058699999997202 | .0006667739999954847 |

To see the full results, check out [results.txt](https://github.com/Andrew-Chen-Wang/postgres-django-icontains-performance/blob/master/results.txt).

## Conclusion

The two biggest factors seemed to be the length of user input
length and the number of objects in the database. There is
also a slight inverse relationship between the two.

This is mainly for finding the most efficient method of querying
using `icontains`. For Donate Anything, there probably won't
be more than a million items. Thus to save space,
we're probably not going to use the SearchVectorField.
It'll make the AWS RDS instance happy. Probably, because if
there are going to be a million items in the database, then
it'd be about time for ElasticSearch.

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