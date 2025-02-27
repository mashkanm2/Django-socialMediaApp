
from django.db import models
from django.utils import timezone

from tripplanapp.apiposts.models import TripLocationModel,TripCategoryModel
from tripplanapp.users.models import BaseUser


class TripModel(models.Model):
    title=models.CharField(max_length=255)
    roade_locations=models.ManyToManyField(TripLocationModel,related_name='trip')
    categorys=models.ManyToManyField(TripCategoryModel,related_name='trip')
    leader=models.ForeignKey(BaseUser,on_delete=models.CASCADE,related_name='trip')
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=False)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.title