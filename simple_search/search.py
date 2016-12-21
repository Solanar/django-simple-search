from django.db import models
from django.contrib import messages

import search


def _get_date_query(
    request, context, df, dt, date_fields
):
    query = models.Q()
    GET = request.GET

    query_date_from_string = GET.get(df, None)
    if query_date_from_string and query_date_from_string.strip():
        context[df] = query_date_from_string

    query_date_to_string = GET.get(dt, None)
    if query_date_to_string and query_date_to_string.strip():
        context[dt] = query_date_to_string

    if query_date_from_string or query_date_to_string:
        try:
            query = search.get_date_query(
                query_date_from_string, query_date_to_string, date_fields
            )
        except search.DoesNotMatchFormat:
            messages.add_message(
                request,
                messages.WARNING,
                "Invalid date. Please use MM/DD/YYYY."
            )

    return query


def _get_query(request, context, q, fields):
    query = models.Q()
    GET = request.GET

    query_string = GET.get(q, None)
    if query_string and query_string.strip():
        context[q] = query_string

        query = search.get_query(query_string, fields)

    return query


def simple_search(
    request,
    context,
    model=None,
    queryset=None,
    query_param=None,
    fields=None,
    date_from_query_param=None,
    date_to_query_param=None,
    date_fields=None
):
    if not model and not queryset:
        raise Exception('Please provide at least one of model or queryset')

    if not fields and not date_fields:
        raise Exception('Please provide at least one of fields or date_fields')

    if not queryset:
        queryset = model.objects.all()

    if fields:
        if not query_param:
            q = 'q'
        else:
            q = query_param

        query = _get_query(request, context, q, fields)
        queryset = queryset.filter(query)

    if date_fields:
        if not date_from_query_param:
            df = 'df'
        else:
            df = date_from_query_param
        if not date_to_query_param:
            dt = 'dt'
        else:
            dt = date_to_query_param

        date_query = _get_date_query(request, context, df, dt, date_fields)
        queryset = queryset.filter(date_query)

    return queryset
