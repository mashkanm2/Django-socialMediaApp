from django.urls import path, include

urlpatterns = [
    # path('blog/', include(('djagosocialmediaapp.blog.urls', 'blog')))
    path("authentication/",include("djagosocialmediaapp.authentication.urls",namespace='authentication')),
    path("user/",include("djagosocialmediaapp.users.urls",namespace='users'))
]
 