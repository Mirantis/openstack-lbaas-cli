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


class Device(base.Resource):
    """Represent load balancer device instance."""

    def __repr__(self):
        return "<Device(%s)>" % self._info


class DeviceManager(base.Manager):
    resource_class = Device
    use_admin_url = True

    def list(self):
        return self._list('/devices', 'devices')

    def create(self, name, type, version, ip, port, user, password, **extra):
        body = {'name': name,
                'type': type,
                'version': version,
                'ip': ip,
                'port': port,
                'user': user,
                'password': password}
        body.update(extra)
        return self._create('/devices', body, 'device')

    def delete(self, device):
        self._delete("/devices/%s" % base.getid(device))

    def get(self, device):
        return self._get("/devices/%s" % base.getid(device), 'device')

    def list_algoritms(self):
        return self._get('/algorithms', 'algorithms', return_raw=True)

    def list_protocols(self):
        return self._get('/protocols', 'protocols', return_raw=True)

    def list_vips(self):
        return self._get('/vips', 'vips', return_raw=True)
