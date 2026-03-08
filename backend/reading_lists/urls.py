from django.urls import path

from .views import (
    ReadingListDetailView,
    ReadingListItemCreateView,
    ReadingListItemDetailView,
    ReadingListListCreateView,
)

urlpatterns = [
    path("", ReadingListListCreateView.as_view(), name="reading-list-list-create"),
    path("<int:pk>/", ReadingListDetailView.as_view(), name="reading-list-detail"),
    path("<int:pk>/items/", ReadingListItemCreateView.as_view(), name="reading-list-item-create"),
    path(
        "<int:pk>/items/<int:item_id>/",
        ReadingListItemDetailView.as_view(),
        name="reading-list-item-detail",
    ),
]
