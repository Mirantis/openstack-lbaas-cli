# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Base utilities to build API operation managers and objects on top of.
"""


def getid(obj):
    """
    Abstracts the common pattern of allowing both an object or an object's ID
    (UUID) as a parameter when dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(object):
    """
    Managers interact with a particular type of API and provide CRUD
    operations for them.
    """
    resource_class = None
    use_admin_url = False

    def __init__(self, api):
        self.api = api

    def _is_admin_url(self, admin_url):
        return self.use_admin_url or admin_url

    def _list(self, url, response_key, obj_class=None, body=None,
              admin_url=False):
        admin_url = self._is_admin_url(admin_url)
        resp, body = self.api.client.json_request('GET', url,
                                                  admin_url=admin_url,
                                                  body=body)

        if obj_class is None:
            obj_class = self.resource_class

        data = body[response_key]
        return [obj_class(self, res, loaded=True) for res in data if res]

    def _delete(self, url, admin_url=False):
        admin_url = self._is_admin_url(admin_url)
        self.api.client.raw_request('DELETE', url, admin_url=admin_url)

    def _update(self, url, body, response_key=None, admin_url=False):
        admin_url = self._is_admin_url(admin_url)
        resp, body = self.api.client.json_request('PUT', url,
                                                  admin_url=admin_url,
                                                  body=body)
        # PUT requests may not return a body
        if body:
            return self.resource_class(self, body[response_key])

    def _create(self, url, body, response_key,
                admin_url=False,
                return_raw=False):
        admin_url = self._is_admin_url(admin_url)
        resp, body = self.api.client.json_request('POST', url,
                                                  admin_url=admin_url,
                                                  body=body)
        if return_raw:
            return body[response_key]
        return self.resource_class(self, body[response_key])

    def _get(self, url, response_key, return_raw=False, admin_url=False):
        admin_url = self._is_admin_url(admin_url)
        resp, body = self.api.client.json_request('GET', url,
                                                  admin_url=admin_url)
        if return_raw:
            return body[response_key]
        return self.resource_class(self, body[response_key])


class Resource(object):
    """
    A resource represents a particular instance of an object (tenant, user,
    etc). This is pretty much just a bag for attributes.

    :param manager: Manager object
    :param info: dictionary representing resource attributes
    :param loaded: prevent lazy-loading if set to True
    """
    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def _add_details(self, info):
        for (k, v) in info.iteritems():
            setattr(self, k, v)

    def __getattr__(self, k):
        if k not in self.__dict__:
            #NOTE(bcwaldon): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)

            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                                                                k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    def get_info(self):
        if not self.is_loaded():
            self.get()
        if self._info:
            return self._info.copy()
        return {}

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.id)
        if new:
            self._info = new._info
            self._add_details(new._info)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if hasattr(self, 'id') and hasattr(other, 'id'):
            return self.id == other.id
        return self._info == other._info

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val
