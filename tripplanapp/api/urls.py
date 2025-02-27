from django.urls import path, include

urlpatterns = [
    path("auth/",include(("tripplanapp.authentication.urls", 'auth'))),
    path("user/",include(("tripplanapp.users.urls",'users'))),
    path("post/",include(("tripplanapp.apiposts.urls",'apiposts'))),
    path("trips/",include(("tripplanapp.trips.urls",'trips'))),
]
