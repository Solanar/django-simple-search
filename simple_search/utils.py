import re
from datetime import datetime

from django.utils import timezone
from django.db import models


def normalize_query(
    query_string,
    # replace whitespace that is 2 or more in length
    normspace=re.compile(r'\s{2,}').sub,
    # find all words bounded by whitespace (group 1) or by quotes (group 0)
    findterms=re.compile(r'"([^"]+)"|(\S+)').findall
):
    """Splits the query string in individual keywords.

    Gets rid of unnecessary spaces and grouping quoted words together.

    Example:

    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    """

    return [
        # replace whitespace that is 2 or more characters in length with
        #  a single space
        normspace(' ', (term[0] or term[1]).strip())
        for term in findterms(query_string)
    ]


def get_query(query_string, search_fields, exact=False):
    """Returns a query, that is a combination of exact or icontains Q objects.

    That combination aims to search keywords within a model
    by testing the given search fields.

    """

    query = models.Q()  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = models.Q()  # Query to search for a given term in each field
        for field_name in search_fields:
            if exact:
                q = models.Q(**{"%s" % field_name: term})
            else:
                q = models.Q(**{"%s__icontains" % field_name: term})

            or_query = or_query | q

        query = query & or_query

    return query


class DoesNotMatchFormat(BaseException):
    pass


def get_date_query(
    query_date_from_string,
    query_date_to_string,
    search_fields,
    date_format='%m/%d/%Y'
):
    """Returns a query, that is a combination of range, lte or gte Q objects.

    That combination aims to search dates within a model
    by testing the given search fields.

    """

    if query_date_from_string:
        try:
            # parse datetime
            date_from = datetime.strptime(
                str(query_date_from_string), date_format
            )
            # make timezone aware
            term_from = timezone.make_aware(
                date_from, timezone.get_current_timezone()
            )
        except ValueError as e:
            # query_date_from_string does not match date_format
            raise DoesNotMatchFormat(str(e))
    else:
        term_from = None
    if query_date_to_string:
        try:
            # parse datetime
            date_to = datetime.strptime(
                str(query_date_to_string), date_format
            )
            # make timezone aware
            term_to = timezone.make_aware(
                date_to, timezone.get_current_timezone()
            )
        except ValueError as e:
            # query_date_to_string does not match date_format
            raise DoesNotMatchFormat(str(e))
    else:
        term_to = None

    if not term_from and not term_to:
        raise Exception('Please provide at least one date')

    or_query = models.Q()  # Query to search for a given term in each field
    for field_name in search_fields:
        if term_from and term_to:
            q = models.Q(**{"%s__range" % field_name: [term_from, term_to]})
        elif term_from:
            q = models.Q(**{"%s__gte" % field_name: term_from})
        elif term_to:
            q = models.Q(**{"%s__lte" % field_name: term_to})
        else:
            raise Exception('Please provide at least one date')

        or_query = or_query | q

    return or_query


def get_choice_query(choice_list, choice_field):
    query = models.Q(**{"%s__in" % choice_field: choice_list})

    return query


def get_bool_query(query_bool_value, bool_field):
    query = models.Q(**{"%s" % bool_field: query_bool_value})

    return query
