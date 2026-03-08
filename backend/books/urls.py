from django.urls import path

from .views import BookDeleteView, BookDetailView, BookListCreateView

urlpatterns = [
    path("", BookListCreateView.as_view(), name="book-list-create"),
    path("<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("<int:pk>/delete/", BookDeleteView.as_view(), name="book-delete"),
]
