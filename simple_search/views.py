from django.views import generic

from . import search


class SearchListView(generic.ListView):
    search_fields = []
    search_date_fields = []

    def get_search_fields(self):
        return self.search_fields

    def get_search_date_fields(self):
        return self.search_date_fields

    def get_context_data(self, **kwargs):
        search_fields = self.get_search_fields()
        search_date_fields = self.get_search_date_fields()

        if not search_fields and not search_date_fields:
            raise Exception(
                'Please define search_fields, search_date_fields, or override'
                ' get_search_fields() or get_search_date_fields().'
            )

        context = super().get_context_data(**kwargs)

        context['object_list'] = search.simple_search(
            self.request,
            context=context,
            queryset=context['object_list'],
            fields=search_fields,
            date_fields=search_date_fields,
        )

        return context
