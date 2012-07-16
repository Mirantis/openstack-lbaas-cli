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


class Node(base.Resource):
    """Represent real server instance."""

    def __repr__(self):
        return "<Node(%s)>" % self._info


class NodeManager(base.Manager):
    resource_class = Node

    def create(self, lb, name, type, address, port, weight, status,
               **extra):
        node = {'name': name,
                'type': type,
                'address': address,
                'port': port,
                'weight': weight,
                'status': status}
        node.update(extra)
        body = {'nodes': [node]}
        # XXX(akscram): create only one node at one time
        nodes_raw = self._create("/loadbalancers/%s/nodes" % (base.getid(lb),),
                                 body, 'nodes', return_raw=True)
        return self.resource_class(self, nodes_raw[0])

    def update(self, lb, node,
               name=None, type=None, address=None, port=None, weight=None,
               **extra):
        body = {}
        if name is not None:
            body['name'] = name
        if type is not None:
            body['type'] = type
        if address is not None:
            body['address'] = address
        if port is not None:
            body['port'] = port
        if weight is not None:
            body['weight'] = weight
        body.update(extra)
        return self._update("/loadbalancers/%s/nodes/%s" % (base.getid(lb),
                                                            base.getid(node)),
                            body, 'nodes')

    def update_status(self, lb, node, status):
        return self._update("/loadbalancers/%s/nodes/%s/%s" %
                                (base.getid(lb), base.getid(node), status),
                            'loadbalancers')

    def delete(self, lb, node):
        self._delete("/loadbalancers/%s/nodes/%s" % (base.getid(lb),
                                                     base.getid(node)))

    def nodes_for_lb(self, lb):
        return self._list("/loadbalancers/%s/nodes" % (base.getid(lb),),
                          'nodes')
