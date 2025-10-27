from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_url = models.URLField(blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)

    # Override default groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Doordash(models.Model):
    url = models.TextField()
    restaurant_id = models.IntegerField()
    restaurant_name = models.TextField()
    restaurant_name_lower = models.TextField()
    breadcrumb = models.TextField()
    street_address = models.TextField()
    city = models.TextField()
    state = models.TextField()
    country = models.TextField()
    phone = models.BigIntegerField()
    star_rating = models.FloatField()
    reviews_count = models.IntegerField()
    price_range = models.TextField()
    cuisine1 = models.TextField()
    opening_hours = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    display_address = models.TextField()
    category = models.TextField()
    item_name = models.TextField()
    item_name_lower = models.TextField()
    item_description = models.TextField()
    item_image = models.TextField()
    item_price = models.TextField()

    class Meta:
        db_table = 'doordash'  # Ensure it maps to the existing table in MySQL

    def __str__(self):
        return self.restaurant_name
