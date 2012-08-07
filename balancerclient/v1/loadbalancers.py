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


class LoadBalancer(base.Resource):
    """Represent load balancer instance."""

    def __repr__(self):
        return "<LoadBalancer(%s)>" % self._info


class LoadBalancerManager(base.Manager):
    resource_class = LoadBalancer

    def list(self):
        return self._list('/loadbalancers', 'loadbalancers')

    def create(self, name, algorithm, protocol, **extra):
        body = {'name': name,
                'algorithm': algorithm,
                'protocol': protocol}
        body.update(extra)
        return self._create('/loadbalancers', body, 'loadbalancer')

    def delete(self, lb):
        self._delete("/loadbalancers/%s" % (base.getid(lb),))

    def get(self, lb):
        return self._get("/loadbalancers/%s" % (base.getid(lb),),
                         'loadbalancer')

    def get_for_vm(self, server):
        return self._get("/loadbalancers/find_for_VM/%s" %
                         (base.getid(server),), 'loadbalancers')

    def update(self, lb, name=None, algorithm=None, protocol=None,
               **extra):
        body = {}
        if name:
            body['name'] = name
        if algorithm:
            body['algorithm'] = algorithm
        if protocol:
            body['protocol'] = protocol
        body.update(extra)
        return self._update("/loadbalancers/%s" % (base.getid(lb),), body,
                            'loadbalancer')

    def list_nodes(self, lb):
        return self.api.nodes.nodes_for_lb(lb)

    def list_probes(self, lb):
        return self.api.probes.probes_for_lb(lb)

    def list_stickies(self, lb):
        return self.api.stickies.stickies_for_lb(lb)
