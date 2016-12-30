from django.db import models
from django.contrib import messages
from django import http

from . import utils


def get_choice_query(request, choice_query_param, context=None):
    query = models.Q()
    GET = request.GET

    query_choice_list = GET.getlist(choice_query_param, [])
    if query_choice_list:
        if context:
            context[choice_query_param] = query_choice_list

        choice_field = choice_query_param
        query = utils.get_choice_query(query_choice_list, choice_field)

    return query


def get_date_query(
    request, date_from_query_param, date_to_query_param, date_fields,
    context=None, human_readable_date_format='MM/DD/YYYY'
):
    query = models.Q()
    GET = request.GET

    query_date_from_string = GET.get(date_from_query_param, '').strip()
    query_date_to_string = GET.get(date_to_query_param, '').strip()
    if query_date_from_string or query_date_to_string:
        if context:
            if query_date_from_string:
                context[date_from_query_param] = query_date_from_string

            if query_date_to_string:
                context[date_to_query_param] = query_date_to_string

        try:
            query = utils.get_date_query(
                query_date_from_string, query_date_to_string, date_fields
            )
        except utils.DoesNotMatchFormat:
            if isinstance(request, http.HttpRequest):
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Invalid date. Please use {}.".format(
                        human_readable_date_format
                    )
                )
            else:
                # TODO: how to handle django rest framework requests
                pass

    return query


def get_query(request, query_param, fields, context=None):
    query = models.Q()
    GET = request.GET

    query_string = GET.get(query_param, '').strip()
    if query_string:
        if context:
            context[query_param] = query_string

        query = utils.get_query(query_string, fields)

    return query


def simple_search(
    request,
    context=None,
    model=None,
    queryset=None,
    query_param='q',
    fields=None,
    date_from_query_param='df',
    date_to_query_param='dt',
    date_fields=None,
    choice_fields=None
):
    if not model and not queryset:
        raise Exception('Please provide at least one of model or queryset')

    if not fields and not date_fields and not choice_fields:
        raise Exception(
            'Please provide at least one of fields, date_fields, '
            'or choice_fields'
        )

    if not queryset:
        queryset = model.objects.all()

    if fields:
        query = get_query(request, query_param, fields, context)
        queryset = queryset.filter(query)

    if date_fields:
        date_query = get_date_query(
            request,
            date_from_query_param,
            date_to_query_param,
            date_fields,
            context
        )
        queryset = queryset.filter(date_query)

    if choice_fields:
        for choice_field in choice_fields:
            choice_query = get_choice_query(
                request, choice_field, context
            )
            queryset = queryset.filter(choice_query)

    return queryset
