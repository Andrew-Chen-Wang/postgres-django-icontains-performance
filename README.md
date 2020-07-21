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

|                      | 20,000               | 100,000              | 200,000              | 370,099              |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .0020984089619000036 | .001988032292700123  | .0018991238057999682 | .002431822135300274  |
| SearchVectorField    | .0018781357522999987 | .0018380841300998838 | .0018222256922999236 | .0020044095713000957 |
| Char + Index         | .0019768946458000114 | .001993863645300016  | .002191165284899802  | .002203354655999294  |
| SearchVector + Index | .0018827794286000725 | .001803563312999941  | .0028036326952002527 | .0020528471941995575 |
| BTree Index (bytes)  | 737280               | 4038656              | 7987200              | 14426112             |
| GIN Index (bytes)    | 1744896              | 6807552              | 8626176              | 15204352             |

The following are the results for a four letter query using `icontains`.

|                      | 20,000               | 100,000              | 200,000              | 370,099              |
|----------------------|----------------------|----------------------|----------------------|----------------------|
| CharField            | .0018526022455000173 | .0019125986364002727 | .002491743599299855  | .002018236057499246  |
| SearchVectorField    | .0020149282166999783 | .0018530558955002902 | .0022240866331000573 | .0018321708575997832 |
| Char + Index         | .001893137184600016  | .0019434230315999229 | .002137830329800192  | .0019526920810996671 |
| SearchVector + Index | .0018650680977999798 | .0017777047066997965 | .0023440439428003    | .001942467717500449  |
| BTree Index (bytes)  | 737280               | 4038656              | 7987200              | 14426112             |
| GIN Index (bytes)    | 1744896              | 6807552              | 8626176              | 15204352             |

After multiple experiments, the index size stays relatively the same, except for the first 100 thousand.

To see the full results, check out [results.txt](https://github.com/Andrew-Chen-Wang/postgres-django-icontains-performance/blob/master/results.txt).

## Conclusion

The two biggest factors seemed to be the length of user input
and the number of objects in the database.

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