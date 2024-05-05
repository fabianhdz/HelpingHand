from django.db import models
from django.contrib.auth.models import User
import uuid


class Language(models.Model):
    name = models.CharField(max_length=15)
    users = models.ManyToManyField(User, related_name='languages')


class Skill(models.Model):
    name = models.CharField(max_length=15)
    users = models.ManyToManyField(User, related_name='skills')

    def __str__(self):
        return self.name


class Location(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, through='Post')

    def __str__(self):
        return self.name


class TrustFactor(models.Model):
    total = models.IntegerField()
    rating = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # on_delete or referential integrity


class Rating(models.Model):
    average = models.FloatField()
    total = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    confirmation_number = models.CharField(max_length=36, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Appointment #{self.confirmation_number} for {self.post}"


class Role(models.Model):
    ROLE_CHOICES = [
        ('provider', 'Provider'),
        ('client', 'Client'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES)
    users = models.ManyToManyField(User, through='Post', related_name='roles')

    def __str__(self):
        return self.name


class Post(models.Model):
    date = models.DateTimeField()
    price_range = models.FloatField()
    expiration_date = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Foreign key to Role
    description = models.TextField()
    is_active = models.BooleanField(default=True)  # New posts are active by default


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.BigIntegerField()
    language = models.CharField(max_length=15)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='profile')
    skills = models.ManyToManyField(Skill, related_name='profiles')  # associate skills with profiles
