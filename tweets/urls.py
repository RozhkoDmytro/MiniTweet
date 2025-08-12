from django.urls import path
from . import views

app_name = "tweets"

urlpatterns = [
    # CRUD operations
    path("", views.tweet_list, name="tweet_list"),
    path("create/", views.tweet_create, name="tweet_create"),
    path("<int:pk>/", views.tweet_detail, name="tweet_detail"),
    path("<int:pk>/update/", views.tweet_update, name="tweet_update"),
    path("<int:pk>/delete/", views.tweet_delete, name="tweet_delete"),
    path("<int:pk>/reply/", views.tweet_reply, name="tweet_reply"),
]
