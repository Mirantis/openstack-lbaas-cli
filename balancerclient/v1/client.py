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

from balancerclient.common import client
from . import devices
from . import loadbalancers
from . import nodes
from . import probes
from . import stickies
from . import vips


class HTTPClient(client.HTTPClient):
    def __init__(self, endpoint=None, token=None, **kwargs):
        if endpoint and not token:
            self.user_endpoint = endpoint
            endpoint = None
        else:
            self.user_endpoint = None
        super(HTTPClient, self).__init__(
                endpoint=endpoint, token=token, **kwargs)

    def _get_endpoint(self, admin_url=False):
        if self.user_endpoint:
            if admin_url:
                return self.user_endpoint
            else:
                return self.user_endpoint + '/' + self.auth_tenant_id
        else:
            return super(HTTPClient, self)._get_endpoint(admin_url)


class Client(object):
    """Client for the OpenStack LBaaS v1 API.

    :param string endpoint: A user-supplied endpoint URL for the balancer
                            service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, **kwargs):
        self.client = HTTPClient(**kwargs)
        self.devices = devices.DeviceManager(self)
        self.loadbalancers = loadbalancers.LoadBalancerManager(self)
        self.nodes = nodes.NodeManager(self)
        self.probes = probes.ProbeManager(self)
        self.stickies = stickies.StickyManager(self)
        self.vips = vips.VIPManager(self)
