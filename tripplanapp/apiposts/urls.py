from django.urls import path
from .apis import ImageUploadView,PostView,PostDetailView,VoteView,CommandView,ReplayView

app_name='apiposts'
urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('post/', PostView.as_view(), name='post-view'),
    path('postview/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
]
 