from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    available_margin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    used_margin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'

    objects = MyUserManager()

    def __str__(self):
        return self.email
    
class user_otps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField(max_length=6)
    def __str__(self):
        return str(self.user)


class stocks(models.Model):
    stock_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12,decimal_places=2,default=0)
    open = models.BooleanField(default=False)
    graph = models.DecimalField(max_digits=4,decimal_places=2,default=0)

    def __str__(self):
        return str(self.stock_name)

class Buy(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    stock = models.ForeignKey(stocks,on_delete=models.CASCADE)
    id_mis = models.BooleanField(default=True)
    on_nrml = models.BooleanField(default=False)
    qty = models.PositiveIntegerField(default=0)
    lots = models.DecimalField(max_digits=15,decimal_places = 2,default=0)
    market = models.BooleanField(default=True)
    limit = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=50,decimal_places = 2,default=0)
    def __str__(self):
        return str(self.stock.stock_name)
class Sell(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(stocks,on_delete=models.CASCADE)
    id_mis = models.BooleanField(default=True)
    on_nrml = models.BooleanField(default=False)
    qty = models.PositiveIntegerField(default=0)
    lots = models.DecimalField(max_digits=15,decimal_places = 2,default=0)
    market = models.BooleanField(default=True)
    limit = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=50,decimal_places = 2,default=0)
    def __str__(self):
        return str(self.stock.stock_name)