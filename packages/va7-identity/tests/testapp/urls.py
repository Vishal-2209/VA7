from django.urls import path, include

urlpatterns = [
    path("identity/", include("va7.identity.urls")),
]
