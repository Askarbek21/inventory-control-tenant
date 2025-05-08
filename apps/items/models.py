from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category_name']
        db_table = 'category'


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['product_name']
        db_table = 'product'


class Measurement(models.Model):
    measurement_name = models.CharField(max_length=100)

    def __str__(self):
        return self.measurement_name

    class Meta:
        verbose_name_plural = "Measurements"
        db_table = 'measurement'


class ArrivedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    measurement = models.ManyToManyField(Measurement, through='MeasurementArrivedProduct', related_name='measurements')
    date_of_arrived = models.DateTimeField(default=timezone.now)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # office should be here
    def __str__(self):
        return f'{self.product.product_name} - {self.date_of_arrived}'

    class Meta:
        verbose_name_plural = "Arrived Products"
        ordering = ['-date_of_arrived']
        db_table = 'arrived_products'


class Stock(models.Model, ArrivedProduct):
    def __str__(self):
        # After date add market, where product came
        return f'{self.product.product_name} - {self.date_of_arrived} '


class MeasurementArrivedProduct(models.Model):
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number = models.FloatField(validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f'{self.product.product_name} - {self.measurement.measurement_name}'

    class Meta:
        verbose_name_plural = "Measurement Arrived Products"
        db_table = 'measurement_arrived_products'


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
