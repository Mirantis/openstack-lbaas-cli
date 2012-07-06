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
"""
OpenStack Client interface. Handles the REST calls and responses.
"""

import httplib2
import copy
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


logger = logging.getLogger(__name__)


class HTTPClient(httplib2.Http):

    USER_AGENT = 'python-balancerclient'

    def __init__(self, endpoint, token=None, timeout=600, insecure=False):
        super(HTTPClient, self).__init__(timeout=timeout)
        self.endpoint = endpoint
        self.auth_token = token

        # httplib2 overrides
        self.force_exception_to_status_code = True
        self.disable_ssl_certificate_validation = insecure

    def _http_request(self, url, method, **kwargs):
        """ Send an http request with the specified characteristics.

        Wrapper around httplib2.Http.request to handle tasks such as
        setting headers, JSON encoding/decoding, and error handling.
        """
        url = self.endpoint + url

        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', self.USER_AGENT)
        if self.auth_token:
            kwargs['headers'].setdefault('X-Auth-Token', self.auth_token)

        resp, body = super(HTTPClient, self).request(url, method, **kwargs)

        if logger.isEnabledFor(logging.DEBUG):
            utils.http_log(logger, (url, method,), kwargs, resp, body)

        if resp.status in (301, 302, 305):
            # Redirected. Reissue the request to the new location.
            return self._http_request(resp['location'], method, **kwargs)

        return resp, body

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')

        if 'body' in kwargs:
            kwargs['body'] = json.dumps(kwargs['body'])

        resp, body = self._http_request(url, method, **kwargs)

        if body:
            try:
                body = json.loads(body)
            except ValueError:
                logger.debug("Could not decode JSON from body: %s" % body)
        else:
            logger.debug("No body was returned.")
            body = None

        if 400 <= resp.status < 600:
            raise exceptions.from_response(resp, body)

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')

        resp, body = self._http_request(url, method, **kwargs)

        if 400 <= resp.status < 600:
            raise exceptions.from_response(resp, body)

        return resp, body
