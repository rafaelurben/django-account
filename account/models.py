from django.contrib.auth.models import User as DjangoUser


# Create your models here.

# Proxy models

class User(DjangoUser):
    class Meta(DjangoUser.Meta):
        proxy = True
