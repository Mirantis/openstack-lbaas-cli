from .utils import unittest

import mock

from balancerclient.common import client
from balancerclient.v1.loadbalancers import LoadBalancerManager


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
