from django.contrib import admin

from .models import PostModel,PostVoteModel,TripLocationModel,CommentModel,TripCategoryModel,ReplyModel

@admin.register(PostModel)
class PostFormAdmin(admin.ModelAdmin):
    list_display = ('location','user','slug', 'files_urls', 'avg_post_vote')

@admin.register(PostVoteModel)
class PostVoteFormAdmin(admin.ModelAdmin):
    list_display =('post','user','rate')

@admin.register(TripLocationModel)
class TripLocationFormAdmin(admin.ModelAdmin):
    list_display = ('location','latitude','longitude')

@admin.register(TripCategoryModel)
class TripCategoryFormAdmin(admin.ModelAdmin):
    list_display = ('category',)

@admin.register(CommentModel)
class CommentFormAdmin(admin.ModelAdmin):
    list_display = ('user','post','content')

@admin.register(ReplyModel)
class ReplyFormAdmin(admin.ModelAdmin):
    list_display = ('user','comment','content')
