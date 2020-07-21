from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class ItemAbstract(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Assume name is unique
    name = models.CharField(max_length=100)

    name_search = SearchVectorField(null=True)

    class Meta:
        abstract = True


class ItemWithoutIndex(ItemAbstract):
    ...


class Item(ItemAbstract):
    name = models.CharField(max_length=100, unique=True, db_index=False)

    class Meta:
        indexes = (
            models.Index(name="item_name_index", fields=("name",)),
            GinIndex(name="item_name_search_gin_index", fields=("name_search",)),
        )
