from django.views import generic

from . import search


class Search:
    search_fields = []

    def get_search_fields(self):
        return self.search_fields

    def search(self, queryset, context=None):
        search_fields = self.get_search_fields()

        if not search_fields:
            raise Exception(
                'Please define search_fields or override get_search_fields().'
            )

        queryset = search.simple_search(
            self.request,
            queryset=queryset,
            fields=search_fields,
            context=context
        )

        return queryset


class SearchListView(generic.ListView, Search):
    def get_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list', self.object_list)

        context = {}
        queryset = self.search(queryset, context)

        context['object_list'] = queryset

        context.update(kwargs)

        return super().get_context_data(**context)
