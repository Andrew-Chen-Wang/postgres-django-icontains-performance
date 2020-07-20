# Generated by Django 3.0.8 on 2020-07-20 01:36

import django.contrib.postgres.search
import django.contrib.postgres.indexes
from django.db import migrations, models


# Source https://findwork.dev/blog/optimizing-postgres-full-text-search-in-django/
ts_vector_trigger = """
    CREATE TRIGGER item_name_search_update BEFORE INSERT OR UPDATE
    ON public_item FOR EACH ROW EXECUTE FUNCTION
    tsvector_update_trigger(name_search, 'pg_catalog.english', name);
    -- Force triggers to run and populate the text_search column.
    UPDATE public_item set ID = ID;
"""

reverse_ts_vector_trigger = """
    DROP TRIGGER name_search ON public_item;
"""


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('name_search', django.contrib.postgres.search.SearchVectorField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemWithoutIndex',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('name_search', django.contrib.postgres.search.SearchVectorField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='item',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name_search'], name='item_name_search_gin_index'),
        ),
        migrations.RunSQL(ts_vector_trigger, reverse_ts_vector_trigger),
    ]