# -*- coding: utf-8 -*-
import urllib
from urllib.parse import urlparse

import six
from intercom import HttpError
from intercom import utils


OPERATOR_ALIASES = (
    ('exact', '='),
    ('nexact', '!='),
    ('contains', '~'),
    ('ncontains', '!~'),
    ('startswith', '^'),
    ('endswith', '$'),
    ('in', 'IN'),
    ('nin', 'NIN'),
    ('gte', '>'),
    ('lte', '<')
)


class CollectionProxy(six.Iterator):

    def __init__(
            self, client, collection_cls, collection,
            finder_url, finder_params={}, search=False):

        self.client = client

        # resource name
        self.resource_name = utils.resource_class_to_collection_name(collection_cls)

        # resource class
        self.resource_class = collection_cls

        # needed to create class instances of the resource
        self.collection_cls = collection_cls

        # needed to reference the collection in the response
        self.collection = collection

        # the original URL to retrieve the resources
        self.finder_url = finder_url

        # the params to filter the resources
        self.finder_params = finder_params

        # search uses post request
        self.search = search

        # an iterator over the resources found in the response
        self.resources = None

        # a link to the next page of results
        self.next_page = None

        # The cursor used for pagination in order to fetch the next page of results.
        self.starting_after = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.resources is None:
            # get the first page of results
            self.get_first_page()

        # try to get a resource if there are no more in the
        # current resource iterator (StopIteration is raised)
        # try to get the next page of results first
        try:
            resource = six.next(self.resources)
        except StopIteration:
            self.get_next_page()
            resource = six.next(self.resources)

        instance = self.collection_cls(**resource)
        return instance

    def __getitem__(self, index):
        for i in range(index):
            six.next(self)
        return six.next(self)

    def get_first_page(self):
        # get the first page of results
        return self.get_page(self.finder_url, self.finder_params)

    def get_next_page(self):
        # get the next page of results
        return self.get_page(self.next_page)

    def get_page(self, url, params={}):
        # get a page of results
        # from intercom import Intercom

        # if there is no url stop iterating
        if url is None:
            raise StopIteration
        if self.search:
            query = self._get_query_from_params(params)
            response = self.client.post(url, {'query': query})
        else:
            response = self.client.get(url, params)

        if response is None:
            raise HttpError('Http Error - No response entity returned')
        collection = response['data']
        # if there are no resources in the response stop iterating
        if collection is None:
            raise StopIteration

        # create the resource iterator
        self.resources = iter(collection)
        # grab the next page URL if one exists
        self.next_page = self.extract_next_link(response)

    def paging_info_present(self, response):
        return 'pages' in response and 'type' in response['pages']

    def extract_next_link(self, response):
        # TODO rewrite logic
        if self.paging_info_present(response):
            paging_info = response["pages"]
            if paging_info.get("next"):
                if isinstance(paging_info.get("next"), dict):
                    query_dict = {
                        'starting_after': paging_info.get("next").get('starting_after'),
                        'page': paging_info.get("next").get('page')
                    }
                    query = urllib.parse.urlencode(query_dict)
                    next_link = '{}?{}'.format(self.finder_url, query)
                else:
                    next_parsed = urlparse(paging_info.get("next"))
                    next_link = '{}?{}'.format(next_parsed.path, next_parsed.query)
                return next_link

    def _get_query_from_params(self, params):
        """

        """
        params = params.copy()
        query = {}
        if len(params) > 1:
            query['operator'] = 'AND'
            query['value'] = []
            for key, value in params.items():
                sub_query = self._parse_filter(key, value)
                query['value'].append(sub_query)
        elif len(params) == 1:
            query = self._parse_filter(*params.popitem())
        else:
            return ''

        return query

    def _parse_filter(self, field, value):
        splitted_field = field.split('__')
        field_name = splitted_field[0]
        try:
            operator_alias = splitted_field[1]
        except IndexError:
            operator_alias = 'exact'
        operator = dict(OPERATOR_ALIASES).get(operator_alias)
        if not operator:
            raise ValueError("Incorrect filter operator.")
        query = {
            'field': field_name,
            'operator': operator,
            'value': value
        }
        return query