from rest_framework import viewsets

from . import search


class SearchModelViewSet(viewsets.ModelViewSet):
    search_fields = []
    search_date_fields = []

    def get_search_fields(self):
        return self.search_fields

    def get_search_date_fields(self):
        return self.search_date_fields

    def get_queryset(self):
        search_fields = self.get_search_fields()
        search_date_fields = self.get_search_date_fields()

        if not search_fields and not search_date_fields:
            raise Exception(
                'Please define search_fields, search_date_fields, or override'
                ' get_search_fields() or get_search_date_fields().'
            )

        queryset = super().get_queryset()

        queryset = search.simple_search(
            self.request,
            queryset=queryset,
            fields=search_fields,
            date_fields=search_date_fields,
        )

        return queryset
