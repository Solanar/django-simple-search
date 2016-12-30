from rest_framework import viewsets

from . import views


class SearchModelViewSet(views.Search, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self.search(queryset)

        return queryset
