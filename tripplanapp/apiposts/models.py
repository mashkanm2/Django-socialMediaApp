from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from tripplanapp.users.models import BaseUser

class TripLocationModel(models.Model):
    location = models.CharField(max_length=255,blank=True,null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,db_index=True)

    def __str__(self):
        return self.location

class TripCategoryModel(models.Model):
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.category

class PostModel(models.Model):
    location = models.ForeignKey(TripLocationModel, on_delete=models.CASCADE, null=True, blank=True,related_name='posts')
    user=models.ForeignKey(BaseUser,on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=255)
    files_urls = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    # post_features = ArrayField(models.FloatField(),size=512,)  ## TODO : features of post using AI (postgrsql)
    post_features = models.TextField(blank=True,null=True)     ## TODO : sqlite
    categories = models.ManyToManyField(TripCategoryModel, related_name='posts')
    

    def __str__(self):
        return self.title

class PostVoteModel(models.Model):
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE,related_name='votes')
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='votes')
    rate = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

class CommentModel(models.Model):
    post = models.ForeignKey(PostModel, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE,related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"


class ReplyModel(models.Model):
    comment = models.ForeignKey(CommentModel, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE,related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"
