# -*- coding: utf-8 -*-

from intercom import contact, utils
from intercom.api_operations.filter_mixin import FilterMixin
from intercom.api_operations.find_all import FindAll
from intercom.api_operations.delete import Delete
from intercom.api_operations.save import Save
from intercom.company import Company
from intercom.service.base_service import BaseService


class Contact(BaseService, FindAll, FilterMixin, Delete, Save):

    @property
    def collection_class(self):
        return contact.Contact

    def detach_from_company(self, id, company_id):
        """Detach contact from company
        id - contact id
        company_id - company id
        """
        collection = utils.resource_class_to_collection_name(
            self.collection_class)
        response = self.client.delete("/%s/%s/companies/%s" % (collection, id, company_id), {})
        return Company(**response)

    def attach_the_company(self, id, company_id):
        """Detach contact from company
        id - contact id
        company_id - company id
        """
        collection = utils.resource_class_to_collection_name(
            self.collection_class)
        response = self.client.post("/%s/%s/companies/" % (collection, id), {'id': company_id})
        return Company(**response)
