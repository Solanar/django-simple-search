from django.views import generic

from . import search


class Search:
    search_fields = []
    search_date_fields = []
    search_choice_fields = []

    def get_search_fields(self):
        return self.search_fields

    def get_search_date_fields(self):
        return self.search_date_fields

    def get_search_choice_fields(self):
        return self.search_choice_fields

    def search(self, queryset):
        search_fields = self.get_search_fields()
        search_date_fields = self.get_search_date_fields()
        search_choice_fields = self.get_search_choice_fields()

        not_has_fields = (
            not search_fields and
            not search_date_fields and
            not search_choice_fields
        )
        if not_has_fields:
            raise Exception(
                'Please define '
                'search_fields, search_date_fields, search_choice_fields, '
                'or override '
                'get_search_fields(), get_search_date_fields(),'
                ' get_search_choice_fields().'
            )

        queryset = search.simple_search(
            self.request,
            queryset=queryset,
            fields=search_fields,
            date_fields=search_date_fields,
            choice_fields=search_choice_fields
        )

        return queryset


class SearchListView(generic.ListView, Search):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object_list'] = self.search(context['object_list'])

        return context
