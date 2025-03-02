from django.urls import path, include

urlpatterns = [
    path("user/",include(("tripplanapp.users.urls",'users'))),
    path("post/",include(("tripplanapp.apiposts.urls",'apiposts'))),
    path("trips/",include(("tripplanapp.trips.urls",'trips'))),
]
