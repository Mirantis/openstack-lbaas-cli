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


class Sticky(base.Resource):
    """Represent a persistent session instance."""

    def __repr__(self):
        return "<Sticky(%s)>" % self._info


class StickyManager(base.Manager):
    resource_class = Sticky

    def create(self, lb, name, type, **extra):
        body = {'name': name,
                'type': type}
        body.update(extra)
        return self._create("/loadbalancers/%s/sessionPersistence" %
                            (base.getid(lb),), 'sessionPersistence')

    def delete(self, lb, sticky):
        self._delete("/loadbalancers/%s/sessionPersistence/%s" %
                     (base.getid(lb), base.getid(sticky)))

    def sticky_for_lb(self, lb):
        return self._list("/loadbalancers/%s/sessionPersistence" %
                          (base.getid(lb),), 'sessionPersistence')
