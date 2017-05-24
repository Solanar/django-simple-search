from django.db import models
from django.db.models import fields as models_fields
from django.contrib import messages
from django import http

from . import utils


def get_bool_query(request, bool_query_param, context=None):
    query = models.Q()
    GET = request.GET

    query_bool_string = GET.get(bool_query_param, '')
    if query_bool_string:
        if context:
            context[bool_query_param] = query_bool_string

        bool_field = bool_query_param
        query_bool_string_lower = query_bool_string.lower()
        if query_bool_string_lower == 'true':
            query_bool_value = True
        elif query_bool_string_lower == 'false':
            query_bool_value = False
        else:
            raise Exception(
                'Unhandled bool string {}'.format(query_bool_string)
            )
        query = utils.get_bool_query(query_bool_value, bool_field)

    return query


def get_choice_query(request, choice_query_param, context=None):
    query = models.Q()
    GET = request.GET

    query_choice_list = GET.getlist(choice_query_param, [])
    if any(query_choice_list):  # ignore list of empty str's
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
    fields=None,
    context=None,
    model=None,
    queryset=None,
    query_param='q',
    date_from_query_param='df',
    date_to_query_param='dt',
    text_fields=None,
    date_fields=None,
    choice_fields=None,
    boolean_fields=None,
):
    if not model and queryset is None:
        raise Exception('Please provide at least one of model or queryset')

    no_fields = (
        not fields and
        not text_fields and
        not date_fields and
        not choice_fields and
        not boolean_fields
    )
    if no_fields:
        raise Exception(
            'Please provide fields, text_fields, date_fields, '
            'choice_fields, or boolean_fields'
        )

    if queryset is None:
        queryset = model.objects.all()

    if not model:
        model = queryset.model

    if not fields:
        fields = []
    if not text_fields:
        text_fields = []
    if not date_fields:
        date_fields = []
    if not choice_fields:
        choice_fields = []
    if not boolean_fields:
        boolean_fields = []
    for field_name in fields:
        field = _get_field(field_name, model)

        if field.choices or isinstance(field, models.ForeignKey):
            choice_fields.append(field_name)
            continue

        is_text = (
            isinstance(field, models_fields.CharField) or
            isinstance(field, models_fields.TextField)
        )
        is_bool = (
            isinstance(field, models_fields.BooleanField) or
            isinstance(field, models_fields.NullBooleanField)
        )
        if is_text:
            text_fields.append(field_name)
        elif isinstance(field, models_fields.DateField):
            date_fields.append(field_name)
        elif is_bool:
            boolean_fields.append(field_name)
        else:
            raise Exception('Unhandled field type {}'.format(type(field)))

    if text_fields:
        query = get_query(request, query_param, text_fields, context)
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

    if boolean_fields:
        for bool_field in boolean_fields:
            bool_query = get_bool_query(
                request, bool_field, context
            )
            queryset = queryset.filter(bool_query)

    return queryset


def _get_field(field_name, model):
    if '__' in field_name:
        # traverse relations until we reach the field we're searching against
        field_lookups = field_name.split('__')
        for field_lookup in field_lookups:
            field = model._meta.get_field(field_lookup)
            if field.related_model:
                model = field.related_model
    else:
        field = model._meta.get_field(field_name)

    return field
