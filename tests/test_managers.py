from .utils import unittest

import mock

from balancerclient.common import client
from balancerclient.v1.loadbalancers import LoadBalancerManager
from balancerclient.v1.nodes import NodeManager
from balancerclient.v1.devices import DeviceManager
from balancerclient.v1.probes import ProbeManager


class LoadBalancerManagerTest(unittest.TestCase):
    def setUp(self):
        self.lbs = LoadBalancerManager(mock.Mock())
        self.lb = mock.Mock(id='fakeid')

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_list(self, mock_list):
        self.lbs.list()
        expected = mock.call(self.lbs, '/loadbalancers', 'loadbalancers')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.lbs.create('fake', 'ROUNDROBIN', 'HTTP')
        body = {'name': 'fake',
                'algorithm': 'ROUNDROBIN',
                'protocol': 'HTTP'}
        expected = mock.call(self.lbs, '/loadbalancers', body,
                             'loadbalancers')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.lbs.delete(self.lb)
        expected = mock.call(self.lbs, '/loadbalancers/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        self.lbs.get(self.lb)
        expected = mock.call(self.lbs, '/loadbalancers/fakeid',
                             'loadbalancers')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get_for_vm(self, mock_get):
        vm = mock.Mock(id='vmfakeid')
        self.lbs.get_for_vm(vm)
        expected = mock.call(self.lbs, '/loadbalancers/find_for_VM/vmfakeid',
                             'loadbalancers')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update(self, mock_update):
        self.lbs.update(self.lb, name='fake', algorithm='LEASTCONNECTION',
                        protocol='FTP')
        body = {'name': 'fake',
                'algorithm': 'LEASTCONNECTION',
                'protocol': 'FTP'}
        expected = mock.call(self.lbs, '/loadbalancers/fakeid', body,
                             'loadbalancers')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])


class NodeManagerTest(unittest.TestCase):
    def setUp(self):
        self.nodes = NodeManager(mock.Mock())
        self.node = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.nodes.create(self.lb, 'node1', 'HW', '10.0.0.1', 80, 10, 'ACTIVE')
        body = {'node': {'name': 'node1',
                         'type': 'HW',
                         'address': '10.0.0.1',
                         'port': 80,
                         'weight': 10,
                         'status': 'ACTIVE'}}
        expected = mock.call(self.nodes, '/loadbalancers/lbfakeid/nodes',
                             body, 'node')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update(self, mock_update):
        self.nodes.update(self.lb, self.node, name='node1', type='HW',
                          address='10.0.0.1', port=80, weight=10,
                          status='ACTIVE')
        body = {'name': 'node1',
                'type': 'HW',
                'address': '10.0.0.1',
                'port': 80,
                'weight': 10,
                'status': 'ACTIVE'}
        expected = mock.call(self.nodes,
                             '/loadbalancers/lbfakeid/nodes/fakeid',
                             body, 'nodes')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update_status(self, mock_update):
        self.nodes.update_status(self.lb, self.node, 'FAKESTATUS')
        expected = mock.call(self.nodes,
                             '/loadbalancers/lbfakeid/nodes/fakeid/FAKESTATUS',
                             'loadbalancers')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.nodes.delete(self.lb, self.node)
        expected = mock.call(self.nodes,
                             '/loadbalancers/lbfakeid/nodes/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_nodes_for_lb(self, mock_list):
        self.nodes.nodes_for_lb(self.lb)
        expected = mock.call(self.nodes, '/loadbalancers/lbfakeid/nodes',
                             'nodes')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])


class DeviceManagerTest(unittest.TestCase):
    def setUp(self):
        self.devices = DeviceManager(mock.Mock())
        self.device = mock.Mock(id='fakeid')

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_list(self, mock_list):
        self.devices.list()
        expected = mock.call(self.devices, '/devices', 'devices')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.devices.create('device1', 'FAKE', '1.0.0', '10.0.0.1', 22,
                            'fakeuser', 'fakepassword')
        body = {'name': 'device1',
                'type': 'FAKE',
                'version': '1.0.0',
                'ip': '10.0.0.1',
                'port': 22,
                'user': 'fakeuser',
                'password': 'fakepassword'}
        expected = mock.call(self.devices, '/devices', body, 'devices')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.devices.delete(self.device)
        expected = mock.call(self.devices, '/devices/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        self.devices.get(self.device)
        expected = mock.call(self.devices, '/devices/fakeid', 'devices')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])


class ProbeManagerTest(unittest.TestCase):
    def setUp(self):
        self.probes = ProbeManager(mock.Mock())
        self.probe = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.probes.create(self.lb, 'probe1', 'ICMP')
        body = {'name': 'probe1',
                'type': 'ICMP'}
        expected = mock.call(self.probes,
                             '/loadbalancers/lbfakeid/healthMonitoring', body,
                             'healthMonitoring')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.probes.delete(self.lb, self.probe)
        expected = mock.call(self.probes,
                             '/loadbalancers/lbfakeid/healthMonitoring/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_probes_for_lb(self, mock_list):
        self.probes.probes_for_lb(self.lb)
        expected = mock.call(self.probes,
                             '/loadbalancers/lbfakeid/healthMonitoring',
                             'healthMonitoring')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])
