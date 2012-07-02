# Copyright 2012 OpenStack LLC.
# All Rights Reserved
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import httplib2
import logging
import os
import urlparse

try:
    import json
except ImportError:
    import simplejson as json
# Python 2.5 compat fix
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl


from . import exceptions
from . import utils
from .service_catalog import ServiceCatalog


_logger = logging.getLogger(__name__)


class HTTPClient(httplib2.Http):
    """Handles the REST calls and responses, include authn"""

    USER_AGENT = 'python-balancerclient'

    def __init__(self, username=None, tenant_name=None,
                 password=None, auth_url=None,
                 token=None, region_name=None, timeout=None,
                 endpoint_url=None, insecure=False,
                 **kwargs):
        super(HTTPClient, self).__init__(timeout=timeout)
        self.username = username
        self.tenant_name = tenant_name
        self.password = password
        self.auth_url = auth_url.rstrip('/') if auth_url else None
        self.region_name = region_name
        self.auth_token = token
        self.content_type = 'application/json'
        self.endpoint_url = endpoint_url
        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

    def _cs_request(self, *args, **kwargs):
        kargs = {}
        kargs.setdefault('headers', kwargs.get('headers', {}))
        kargs['headers']['User-Agent'] = self.USER_AGENT

        if 'content_type' in kwargs:
            kargs['headers']['Content-Type'] = kwargs['content_type']
            kargs['headers']['Accept'] = kwargs['content_type']
        else:
            kargs['headers']['Content-Type'] = self.content_type
            kargs['headers']['Accept'] = self.content_type

        if 'body' in kwargs:
            kargs['body'] = kwargs['body']

        resp, body = self.request(*args, **kargs)

        utils.http_log(_logger, args, kargs, resp, body)
        status_code = self.get_status_code(resp)
        if status_code != 200:
            raise exception.from_response(resp, body)
        return resp, body

    def do_request(self, url, method, **kwargs):
        if not self.endpoint_url:
            self.authenticate()

        # Perform the request once. If we get a 401 back then it
        # might be because the auth token expired, so try to
        # re-authenticate and try again. If it still fails, bail.
        try:
            if self.auth_token:
                kwargs.setdefault('headers', {})
                kwargs['headers']['X-Auth-Token'] = self.auth_token
            resp, body = self._cs_request(self.endpoint_url + url, method,
                                          **kwargs)
            return resp, body
        except exceptions.Unauthorized as ex:
            if not self.endpoint_url:
                self.authenticate()
                resp, body = self._cs_request(
                    self.management_url + url, method, **kwargs)
                return resp, body
            else:
                raise ex

    def _extract_service_catalog(self, body):
        """ Set the client's service catalog from the response data. """
        try:
            self.service_catalog = ServiceCatalog(body['access'])
            token = self.service_catalog.get_token()
            self.auth_token = token['id']
            self.auth_tenant_id = token.get('tenant_id')
            self.auth_user_id = token.get('user_id')
        except KeyError:
            raise exceptions.AuthorizationFailure()
        self.endpoint_url = self.service_catalog.url_for(
            attr='region', filter_value=self.region_name,
            endpoint_type='adminURL')

    def authenticate(self):
        body = {'auth': {'passwordCredentials':
                                               {'username': self.username,
                                                'password': self.password},
                         'tenantName': self.tenant_name}}

        token_url = self.auth_url + "/tokens"

        # Make sure we follow redirects when trying to reach Keystone
        tmp_follow_all_redirects = self.follow_all_redirects
        self.follow_all_redirects = True
        try:
            resp, body = self._cs_request(token_url, "POST",
                                          body=json.dumps(body),
                                          content_type="application/json")
        finally:
            self.follow_all_redirects = tmp_follow_all_redirects
        status_code = self.get_status_code(resp)
        if status_code != 200:
            raise exceptions.Unauthorized(message=body)
        if body:
            try:
                body = json.loads(body)
            except ValueError:
                pass
        else:
            body = None
        self._extract_service_catalog(body)

    def get_status_code(self, response):
        """
        Returns the integer status code from the response, which
        can be either a Webob.Response (used in testing) or httplib.Response
        """
        if hasattr(response, 'status_int'):
            return response.status_int
        else:
            return response.status
