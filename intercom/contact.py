# -*- coding: utf-8 -*-

from intercom.traits.api_resource import Resource
from intercom.traits.incrementable_attributes import IncrementableAttributes


class Contact(Resource, IncrementableAttributes):

    update_verb = 'post'
    identity_vars = ['id', 'email', 'user_id']
    filter_source = 'contacts/search'

    @property
    def flat_store_attributes(self):
        return ['custom_attributes']

    def __str__(self):
        return f"{self.name} - {self.id}"
