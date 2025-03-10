
from django.db.models import QuerySet
from .models import PostModel,PostVoteModel,TripCategoryModel,TripLocationModel
from tripplanapp.users.models import BaseUser

def post_detail(*,slug,user:BaseUser) -> PostModel:
    ## TODO : add blucker user to return None
    post = PostModel.objects.get(slug=slug)
    return post

def get_user_post():
    pass

def post_list(*,filters=None,user:BaseUser) -> QuerySet[PostModel]:
    filters=filters or {}
    qs=PostModel.objects.filter(**filters)
    return qs


def get_list_of_userposts():
    pass


def get_locationFilter_posts():
    pass

def get_categoryFilter_posts():
    pass

def get_postComments():
    pass

def get_commentReplyes():
    pass

def get_featureSimilarityPosts():
    pass
