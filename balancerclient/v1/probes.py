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

from balancerclient.common import base


class Probe(base.Resource):
    """Represent health monitoring instance."""

    def __repr__(self):
        return "<Probe(%s)>" % self._info


class ProbeManager(base.Manager):
    resource_class = Probe

    def create(self, lb, name, type, **extra):
        probe = {'name': name,
                 'type': type}
        probe.update(extra)
        body = {'healthMonitoring': probe}
        return self._create("/loadbalancers/%s/healthMonitoring" %
                                (base.getid(lb),),
                            body, 'healthMonitoring')

    def get(self, lb, probe):
        return self._get("/loadbalancers/%s/healthMonitoring/%s" %
                            (base.getid(lb), base.getid(probe)),
                         'healthMonitoring')

    def delete(self, lb, probe):
        self._delete("/loadbalancers/%s/healthMonitoring/%s" %
                     (base.getid(lb), base.getid(probe)))

    def list(self, lb):
        return self._list("/loadbalancers/%s/healthMonitoring" %
                              (base.getid(lb),),
                          'healthMonitoring')
