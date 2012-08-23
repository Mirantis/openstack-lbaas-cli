import unittest2
import mock

from balancerclient.common import client
from balancerclient.v1.client import Client
from balancerclient.v1.loadbalancers import LoadBalancerManager
from balancerclient.v1.nodes import NodeManager
from balancerclient.v1.devices import DeviceManager
from balancerclient.v1.probes import ProbeManager
from balancerclient.v1.stickies import StickyManager
from balancerclient.v1.vips import VIPManager


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
        self.assertTrue(hasattr(client, 'vips'))


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
        self.lbs.create('fake', 'ROUNDROBIN', 'HTTP', 'vipfake', '10.0.0.1',
                        '255.255.255.0', 80)
        body = {'name': 'fake',
                'algorithm': 'ROUNDROBIN',
                'protocol': 'HTTP',
                'virtualIps': [{'name': 'vipfake',
                                'address': '10.0.0.1',
                                'mask': '255.255.255.0',
                                'port': 80}]}
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
                             'loadbalancer')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])


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
                           'condition': 'ACTIVE'}]}
        expected = mock.call(self.nodes, '/loadbalancers/lbfakeid/nodes',
                              body, 'nodes', return_raw=True)
        self.assertTrue(mock_create.called)
        self.assertNotEqual(mock_create.mock_calls, [])
        self.assertEqual(mock_create.mock_calls[0], expected)

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update(self, mock_update):
        self.nodes.update(self.lb, self.node, name='node1', type='HW',
                          address='10.0.0.1', port=80, weight=10,
                          condition='ACTIVE')
        body = {'name': 'node1',
                'type': 'HW',
                'address': '10.0.0.1',
                'port': 80,
                'weight': 10,
                'condition': 'ACTIVE'}
        expected = mock.call(self.nodes,
                             '/loadbalancers/lbfakeid/nodes/fakeid',
                             body, 'node')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update_condition(self, mock_update):
        self.nodes.update_condition(self.lb, self.node, 'FAKECONDITION')
        expected = mock.call(self.nodes,
                       '/loadbalancers/lbfakeid/nodes/fakeid/FAKECONDITION',
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
    def test_nodes_list(self, mock_list):
        self.nodes.list(self.lb)
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
        expected = mock.call(self.devices, '/devices', body, 'device')
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

    @mock.patch('balancerclient.common.base.Manager._get')
    def test_list_algorithms(self, mock_get):
        self.devices.list_algoritms()
        expected = mock.call('/algorithms', 'algorithms', return_raw=True)
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._get')
    def test_list_protocols(self, mock_get):
        self.devices.list_protocols()
        expected = mock.call('/protocols', 'protocols', return_raw=True)
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])


class TestProbeManager(unittest2.TestCase):
    def setUp(self):
        self.probes = ProbeManager(mock.Mock())
        self.probe = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        mock_get.return_value = mock_probe = mock.Mock()
        probe = self.probes.get(self.lb, self.probe)
        expected = mock.call(self.probes,
                             '/loadbalancers/lbfakeid/healthMonitoring/fakeid',
                             'healthMonitoring')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])
        self.assertEqual(probe, mock_probe)

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.probes.create(self.lb, 'probe1', 'ICMP')
        body = {'healthMonitoring': {'name': 'probe1',
                                     'type': 'ICMP'}}
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
    def test_probes_list(self, mock_list):
        self.probes.list(self.lb)
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

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        mock_get.return_value = mock_sticky = mock.Mock()
        sticky = self.stickies.get(self.lb, self.sticky)
        expected = mock.call(self.stickies,
                        '/loadbalancers/lbfakeid/sessionPersistence/fakeid',
                        'sessionPersistence')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])
        self.assertEqual(sticky, mock_sticky)

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
    def test_sticky_list(self, mock_list):
        self.stickies.list(self.lb)
        expected = mock.call(self.stickies,
                             '/loadbalancers/lbfakeid/sessionPersistence',
                             'sessionPersistence')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])


class TestVIPManager(unittest2.TestCase):
    def setUp(self):
        self.vips = VIPManager(mock.Mock())
        self.vip = mock.Mock(id='fakeid')
        self.lb = mock.Mock(id='lbfakeid')

    @mock.patch('balancerclient.common.base.Manager._create', autospec=True)
    def test_create(self, mock_create):
        self.vips.create(self.lb, 'vip100', '10.0.0.1', '255.255.255.0', 80,
                         vlan=100)
        body = {'virtualIp': {'name': 'vip100',
                              'address': '10.0.0.1',
                              'mask': '255.255.255.0',
                              'port': 80,
                              'VLAN': 100}}
        expected = mock.call(self.vips,
                             '/loadbalancers/lbfakeid/virtualIps',
                             body,
                             'virtualIp')
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._delete', autospec=True)
    def test_delete(self, mock_delete):
        self.vips.delete(self.lb, self.vip)
        expected = mock.call(self.vips,
                        '/loadbalancers/lbfakeid/virtualIps/fakeid')
        self.assertTrue(mock_delete.called)
        self.assertEqual(mock_delete.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._update', autospec=True)
    def test_update(self, mock_update):
        self.vips.update(self.lb, self.vip,
                         name='vlan100-80', address='10.2.0.1')
        body = {'name': 'vlan100-80',
                'address': '10.2.0.1'}
        expected = mock.call(self.vips,
                        '/loadbalancers/lbfakeid/virtualIps/fakeid',
                        body,
                        'virtualIp')
        self.assertTrue(mock_update.called)
        self.assertEqual(mock_update.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._get', autospec=True)
    def test_get(self, mock_get):
        self.vips.get(self.lb, self.vip)
        expected = mock.call(self.vips,
                             '/loadbalancers/lbfakeid/virtualIps/fakeid',
                             'virtualIp')
        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.mock_calls, [expected])

    @mock.patch('balancerclient.common.base.Manager._list', autospec=True)
    def test_list(self, mock_list):
        self.vips.list(self.lb)
        expected = mock.call(self.vips, '/loadbalancers/lbfakeid/virtualIps',
                             'virtualIps')
        self.assertTrue(mock_list.called)
        self.assertEqual(mock_list.mock_calls, [expected])
