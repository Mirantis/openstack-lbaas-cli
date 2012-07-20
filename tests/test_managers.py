import unittest2
import mock

from balancerclient.common import client
from balancerclient.v1.client import Client
from balancerclient.v1.loadbalancers import LoadBalancerManager
from balancerclient.v1.nodes import NodeManager
from balancerclient.v1.devices import DeviceManager
from balancerclient.v1.probes import ProbeManager
from balancerclient.v1.stickies import StickyManager


class TestClient(unittest2.TestCase):
    @mock.patch('httplib2.Http', autospec=True)
    def test_client(self, mock_http):
        client = Client(endpoint='http://localhost:8181/fakes',
                        token='faketoken')
        self.assertTrue(hasattr(client, 'devices'))
        self.assertTrue(hasattr(client, 'loadbalancers'))
        self.assertTrue(hasattr(client, 'nodes'))
        self.assertTrue(hasattr(client, 'probes'))
        self.assertTrue(hasattr(client, 'stickies'))


class TestLoadBalancerManager(unittest2.TestCase):
    def setUp(self):
        self.api = mock.Mock()
        self.lbs = LoadBalancerManager(self.api)
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
                             'loadbalancer')
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
                             'loadbalancer')
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

    def test_list_nodes(self):
        self.lbs.list_nodes(self.lb)
        self.assertTrue(self.api.nodes.nodes_for_lb.called)
        self.assertEqual(self.api.nodes.nodes_for_lb.mock_calls,
                         [mock.call(self.lb)])

    def test_list_probes(self):
        self.lbs.list_probes(self.lb)
        self.assertTrue(self.api.probes.probes_for_lb.called)
        self.assertEqual(self.api.probes.probes_for_lb.mock_calls,
                         [mock.call(self.lb)])

    def test_list_stickies(self):
        self.lbs.list_stickies(self.lb)
        self.assertTrue(self.api.stickies.stickies_for_lb.called)
        self.assertEqual(self.api.stickies.stickies_for_lb.mock_calls,
                         [mock.call(self.lb)])


class TestNodeManager(unittest2.TestCase):
    def setUp(self):
        self.nodes = NodeManager(mock.Mock())
        self.node = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        self.nodes.get(self.lb, self.node)
        expected = mock.call(self.nodes,
                             '/loadbalancers/lbfakeid/nodes/fakeid',
                             'node')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.nodes.create(self.lb, 'node1', 'HW', '10.0.0.1', 80, 10, 'ACTIVE')
        body = {'nodes': [{'name': 'node1',
                           'type': 'HW',
                           'address': '10.0.0.1',
                           'port': 80,
                           'weight': 10,
                           'status': 'ACTIVE'}]}
        expected = mock.call(self.nodes, '/loadbalancers/lbfakeid/nodes',
                              body, 'nodes', return_raw=True)
        self.assertTrue(mock_create.called)
        self.assertNotEqual(mock_create.mock_calls, [])
        self.assertEqual(mock_create.mock_calls[0], expected)

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


class TestDeviceManager(unittest2.TestCase):
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
        expected = mock.call(self.devices, '/devices/fakeid', 'device')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])


class TestProbeManager(unittest2.TestCase):
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


class TestStickyManager(unittest2.TestCase):
    def setUp(self):
        self.stickies = StickyManager(mock.Mock())
        self.sticky = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.stickies.create(self.lb, 'sticky1', 'HTTP')
        body = {'name': 'sticky1',
                'type': 'HTTP'}
        expected = mock.call(self.stickies,
                             '/loadbalancers/lbfakeid/sessionPersistence',
                             body,
                             'sessionPersistence')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.stickies.delete(self.lb, self.sticky)
        expected = mock.call(self.stickies,
                        '/loadbalancers/lbfakeid/sessionPersistence/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_sticky_for_lb(self, mock_list):
        self.stickies.stickies_for_lb(self.lb)
        expected = mock.call(self.stickies,
                             '/loadbalancers/lbfakeid/sessionPersistence',
                             'sessionPersistence')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])
