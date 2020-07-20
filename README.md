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

## Conclusion

This is mainly for finding the most efficient method of querying
using `icontains`. For Donate Anything, there probably won't
be more than a million items. Thus to save space,
we're probably not going to use the SearchVectorField.
It'll make the AWS RDS instance happy. Probably, because if
there are going to be a million items in the database, then
it'd be about time for ElasticSearch.

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