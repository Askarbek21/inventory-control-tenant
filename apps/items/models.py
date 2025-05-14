from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.stores.models import Store
from apps.suppliers.models import Supplier


class Category(models.Model):
    category_name = models.CharField(max_length=200)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category_name']
        db_table = 'category'


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['product_name']
        db_table = 'product'


class Measurement(models.Model):
    measurement_name = models.CharField(max_length=100)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

    def __str__(self):
        return self.measurement_name

    class Meta:
        verbose_name_plural = "Measurements"
        db_table = 'measurement'


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    measurement = models.ManyToManyField(Measurement, through='MeasurementArrivedProductInStore',
                                         related_name='measurements')
    date_of_arrived = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    history_of_prices = models.JSONField(default=dict)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    color = models.CharField(max_length=199, null=True, blank=True)

    def __str__(self):
        return f'{self.product.product_name} -- {self.store.name}'

    class Meta:
        verbose_name_plural = "Stocks"
        ordering = ['-date_of_arrived']
        db_table = 'stock'


class MeasurementArrivedProductInStore(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)

    number = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f'{self.measurement.measurement_name}'

    class Meta:
        verbose_name_plural = "Measurement Arrived Products In Stock"
        db_table = 'measurement_arrived_products_in_stock'


class ArrivedProduct(models.Model):
    data = models.JSONField()

    class Meta:
        verbose_name_plural = "Arrived Products"
        db_table = 'arrived_product'


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
