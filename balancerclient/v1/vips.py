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


class VIP(base.Resource):
    """Represent real server instance."""

    def __repr__(self):
        return "<VIP(%s)>" % (self._info,)


class VIPManager(base.Manager):
    resource_class = VIP

    def list(self, lb):
        return self._list("/loadbalancers/%s/virtualIps" % (base.getid(lb),),
                          'virtualIps')

    def create(self, lb, name, address, mask, port, type=None, vlan=None,
               **extra):
        vip = dict(name=name,
                   address=address,
                   mask=mask,
                   port=port,
                   **extra)
        if type is not None:
            vip['type'] = type
        if vlan is not None:
            vip['VLAN'] = vlan
        body = {'virtualIp': vip}
        return self._create("/loadbalancers/%s/virtualIps" % (base.getid(lb),),
                            body, 'virtualIp')

    def update(self, lb, vip,
               name=None, address=None, mask=None, port=None, type=None,
               vlan=None,
               **extra):
        body = dict(name=name,
                    address=address,
                    mask=mask,
                    port=port,
                    type=type,
                    VLAN=vlan,
                    *extra)
        for key, value in body.items():
            if value is None:
                body.pop(key)
        return self._update("/loadbalancers/%s/virtualIps/%s" %
                                (base.getid(lb), base.getid(vip)),
                            body, 'virtualIp')

    def get(self, lb, vip):
        return self._get("/loadbalancers/%s/virtualIps/%s" %
                             (base.getid(lb), base.getid(vip)),
                         'virtualIp')

    def delete(self, lb, vip):
        return self._delete("/loadbalancers/%s/virtualIps/%s" %
                                (base.getid(lb), base.getid(vip)))
