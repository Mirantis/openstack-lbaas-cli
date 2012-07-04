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


class Client(object):
    """Client for the OpenStack LBaaS v1 API.

    :param string endpoint: A user-supplied endpoint URL for the balancer
                            service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, endpoint, token=None, timeout=600, **kwargs):
        self.http_client = client.HTTPClient(
                endpoint, token=token, timeout=timeout)
        self.devices = devices.DeviceManager(self)
        self.loadbalancers = loadbalancers.LoadBalancerManager(self)
        self.nodes = nodes.NodeManager(self)
        self.probes = probes.ProbeManager(self)
        self.stickies = stickies.StickyManager(self)
