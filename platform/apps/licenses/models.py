from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class License(models.Model):
    key = models.CharField(max_length=64, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    expires_at = models.DateField(null=True, blank=True)
    feature_flags = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.key
