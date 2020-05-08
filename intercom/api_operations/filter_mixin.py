# -*- coding: utf-8 -*-
"""Operation to find all instances of a particular resource."""

from intercom.collection_proxy import CollectionProxy


class FilterMixin(object):
    """A mixin that provides `filter` functionality."""

    proxy_class = CollectionProxy

    def filter(self, **params):
        """Find all instances of the resource based on the supplied filters."""
        collection = self.collection_class.filter_source
        finder_url = "/%s" % (collection,)

        finder_params = params
        return self.proxy_class(
            self.client, self.collection_class, collection,
            finder_url, finder_params, True)
