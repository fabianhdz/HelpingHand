from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.BigIntegerField()
    language = models.CharField(max_length=15)
    address = models.CharField(max_length=50)
    zip_code = models.IntegerField()

    # Example method to access full address
    def full_address(self):
        return f"{self.address}, {self.zip_code}"


class Language(models.Model):
    name = models.CharField(max_length=15)
    users = models.ManyToManyField(User, related_name='languages')


class Skill(models.Model):
    name = models.CharField(max_length=15)
    users = models.ManyToManyField(User, related_name='skills')
    # Related_name: you can get skills for users such user = User.objects.get(id=1)
    # user_skills = user.skills.all()


class Location(models.Model):
    zip_code = models.IntegerField()
    city = models.CharField(max_length=25)
    state = models.CharField(max_length=2)


class Service(models.Model):
    name = models.CharField(max_length=20)
    users = models.ManyToManyField(User, through='Post')


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


class Role(models.Model):
    name = models.CharField(max_length=20)
    users = models.ManyToManyField(User, through='Post', related_name='roles')


class Post(models.Model):
    date = models.DateTimeField()
    price_range = models.FloatField()
    expiration_date = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  # Foreign key to Role
