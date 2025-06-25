from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.stores.models import Store
from apps.suppliers.models import Supplier


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['-id']
        db_table = 'category'


class Measurement(models.Model):
    measurement_name = models.CharField(max_length=100)

    def __str__(self):
        return self.measurement_name

    class Meta:
        verbose_name_plural = "Measurements"
        db_table = 'measurement'
        ordering = ['-id']


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    measurement = models.ManyToManyField(Measurement, through='MeasurementProduct',
                                         related_name='measurements')
    has_color = models.BooleanField(default=False)
    has_kub = models.BooleanField(default=False)
    kub = models.FloatField(max_length=199, null=True, blank=True)

    color = models.CharField(max_length=199, null=True, blank=True)
    history = models.JSONField(null=True, blank=True)
    has_recycling = models.BooleanField(default=False)
    categories_for_recycling = models.ManyToManyField(Category, related_name='recycling_categories',
                                                      blank=True,
                                                      )
    is_list = models.BooleanField(default=False)
    length = models.FloatField(max_length=199, null=True, blank=True)
    static_weight = models.FloatField(max_length=199, null=True, blank=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['-product_name']
        db_table = 'product'


class MeasurementProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    number = models.CharField(max_length=254, null=True, blank=True)
    for_sale = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.measurement.measurement_name}'

    class Meta:
        verbose_name_plural = "Measurement Arrived Products In Stock"
        db_table = 'measurement_arrived_products_in_stock'


class Currency(models.Model):
    currency_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.currency_rate}"

    def save(self, *args, **kwargs):
        if not self.pk and Currency.objects.exists():
            raise ValueError("Только одна валюта может быть сохранена в базе данных.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Currencies"
        db_table = 'currency'
        ordering = ['-id']


def get_currency_rate():
    try:
        return Currency.objects.first()
    except Currency.DoesNotExist:
        return None


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    date_of_arrived = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.FloatField()
    quantity_for_history = models.FloatField(null=True, blank=True)
    exchange_rate = models.ForeignKey(Currency, on_delete=models.CASCADE, default=get_currency_rate, null=True)
    purchase_price_in_uz = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    purchase_price_in_us = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    selling_price_in_us = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    min_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    history_of_prices = models.JSONField(default=dict)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    total_volume = models.FloatField(max_length=199, null=True, blank=True)

    income_weight = models.FloatField(max_length=199, null=True, blank=True)

    def __str__(self):
        return f'{self.product.product_name} -- {self.store.name}'

    def save(self, *args, **kwargs):
        if not self.exchange_rate_id:
            self.exchange_rate = Currency.objects.first()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Stocks"
        ordering = ['-date_of_arrived']
        db_table = 'stock'


class DeletedItems(models.Model):
    model = models.CharField(max_length=230, null=True, blank=True)
    date_of_deleted = models.DateTimeField(default=timezone.now)
    data = models.JSONField()

    def __str__(self):
        return f'{self.model} - {self.date_of_deleted}'

    class Meta:
        verbose_name_plural = "Deleted Items"
        ordering = ['-date_of_deleted']
        db_table = 'deleted_items'
