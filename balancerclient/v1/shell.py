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

from balancerclient.common import utils
from balancerclient.v1 import client


CLIENT_CLASS = client.Client


def extra_args(argument):
    return dict(v.split('=', 1) for v in argument)

# Devices


def do_device_list(cl, args):
    devices = cl.devices.list()
    utils.print_list(devices, ('id', 'name', 'type', 'version', 'ip', 'port',
                               'user', 'password'))


@utils.arg('id', metavar='<device-id>', help='Device ID to display')
def do_device_show(cl, args):
    device = cl.devices.get(args.id)
    utils.print_dict(device._info)


@utils.arg('--name', metavar='<device-name>', required=True,
           help='New device name')
@utils.arg('--type', metavar='<type>', required=True,
           help='Type of the device')
@utils.arg('--version', metavar='<version>', required=True,
           help='Device version')
@utils.arg('--ip', metavar='<ip>', required=True, help='IP address')
@utils.arg('--port', metavar='<port>', required=True, help='Access port')
@utils.arg('--user', metavar='<user>', required=True,
           help='Account name on the device')
@utils.arg('--password', metavar='<password>', required=True,
           help='Account password on the device')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
def do_device_create(cl, args):
    device = cl.devices.create(args.name, args.type, args.version, args.ip,
                               args.port, args.user, args.password,
                               **extra_args(args.extra))
    utils.print_dict(device._info)


@utils.arg('id', metavar='<device-id>', help='Device ID to delete')
def do_device_delete(cl, args):
    cl.devices.delete(args.id)


def do_algorithms_list(cl, args):
    algos = cl.devices.list_algoritms()
    utils.print_flat_list(algos, ['algorithms'])


def do_protocols_list(cl, args):
    protos = cl.devices.list_protocols()
    utils.print_flat_list(protos, ['protocols'])

# LoadBalancers


def do_lb_list(cl, args):
    lbs = cl.loadbalancers.list()
    utils.print_list(lbs, ('id', 'name', 'algorithm', 'protocol'))


@utils.arg('id', metavar='<lb-id>', help='LoadBalancer ID to display')
def do_lb_show(cl, args):
    lb = cl.loadbalancers.get(args.id)
    utils.print_dict(lb.get_info())


@utils.arg('--name', metavar='<lb-name>', required=True, help='New lb name')
@utils.arg('--algorithm', metavar='<algorithm>', required=True,
           help='Algorithm of choosing servers')
@utils.arg('--protocol', metavar='<protocol>', required=True,
           help='Protocol of load balancing')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Load Balancer extra properties')
def do_lb_create(cl, args):
    lb = cl.loadbalancers.create(args.name, args.algorithm, args.protocol,
                                 **extra_args(args.extra))
    utils.print_dict(lb.get_info())


@utils.arg('--name', metavar='<lb-name>', help='Desired new lb name')
@utils.arg('--algorithm', metavar='<algorithm>',
           help='Desired new algorithm')
@utils.arg('--protocol', metavar='<protocol>', help='Desired new protocol')
@utils.arg('id', metavar='<lb-id>', help='LoadBalancer ID to update')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
def do_lb_update(cl, args):
    kwargs = extra_args(args.extra)
    if args.name:
        kwargs['name'] = args.name
    if args.algorithm:
        kwargs['algorithm'] = args.algorithm
    if args.protocol:
        kwargs['protocol'] = args.protocol

    if not len(kwargs):
        print "LoadBalancer not updated, no arguments present."
        return

    try:
        lb = cl.loadbalancers.update(args.id, **kwargs)
        print 'LoadBalancer has been updated.'
        utils.print_dict(lb._info)
    except Exception, e:
        print 'Unable to update loadbalancer: %s' % e
        raise


@utils.arg('id', metavar='<lb-id>', help='LoadBalancer ID to delete')
def do_lb_delete(cl, args):
    cl.loadbalancers.delete(args.id)


# Nodes


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
def do_node_list(cl, args):
    nodes = cl.nodes.list(args.lb_id)
    utils.print_list(nodes, ('id', 'name', 'type', 'address', 'port',
                             'weight', 'condition', 'status'))


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<node-id>', help='Node ID to display')
def do_node_show(cl, args):
    node = cl.nodes.get(args.lb_id, args.id)
    utils.print_dict(node._info)


@utils.arg('--name', metavar='<node-name>', required=True,
           help='New node name')
@utils.arg('--type', metavar='<type>', required=True,
           help='Type of the node')
@utils.arg('--address', metavar='<address>', required=True,
           help='Node address')
@utils.arg('--port', metavar='<port>', required=True, help='Node port')
@utils.arg('--weight', metavar='<weight>', required=True, help='Node weight')
@utils.arg('--condition', metavar='<condition>', required=True,
           help='Node condition')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
           help='Extra properties')
def do_node_create(cl, args):
    node = cl.nodes.create(args.lb_id, args.name, args.type, args.address,
                           args.port, args.weight, args.condition,
                           **extra_args(args.extra))
    utils.print_dict(node._info)


@utils.arg('--name', metavar='<node-name>', help='Desired new node name')
@utils.arg('--type', metavar='<type>', help='Desired new type of the node')
@utils.arg('--address', metavar='<address>', help='Node address')
@utils.arg('--port', metavar='<port>', help='Desired new node port')
@utils.arg('--weight', metavar='<weight>', help='Desired new node weight')
@utils.arg('--condition', metavar='<condition>', help='Node condition')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<node-id>', help='Node ID')
def do_node_update(cl, args):
    kwargs = extra_args(args.extra)
    if args.name:
        kwargs['name'] = args.name
    if args.type:
        kwargs['type'] = args.type
    if args.address:
        kwargs['address'] = args.address
    if args.port:
        kwargs['port'] = args.port
    if args.weight:
        kwargs['weight'] = args.weight
    if args.condition:
        kwargs['condition'] = args.condition

    if not len(kwargs):
        print "Node not updated, no arguments present."
        return

    try:
        node = cl.nodes.update(args.lb_id, args.id, **kwargs)
        print 'Node has been updated.'
        utils.print_dict(node._info)
    except Exception, e:
        print 'Unable to update node: %s' % e
        raise


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<node-id>', help='Node ID')
def do_node_delete(cl, args):
    cl.nodes.delete(args.lb_id, args.id)


# Probes


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
def do_probe_list(cl, args):
    probes = cl.probes.list(args.lb_id)
    utils.print_list(probes, ('id', 'name', 'type'))


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<probe-id>', help='Probe ID to display')
def do_probe_show(cl, args):
    probe = cl.probes.get(args.lb_id, args.id)
    utils.print_dict(probe._info)


@utils.arg('--name', metavar='<probe-name>', required=True,
           help='New probe name')
@utils.arg('--type', metavar='<type>', required=True, help='Type of the probe')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
def do_probe_create(cl, args):
    probe = cl.probes.create(args.lb_id, args.name, args.type,
                             **extra_args(args.extra))
    utils.print_dict(probe._info)


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<probe-id>', help='Probe ID')
def do_probe_delete(cl, args):
    cl.probes.delete(args.lb_id, args.id)


# Stickies


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
def do_sticky_list(cl, args):
    stickies = cl.stickies.list(args.lb_id)
    utils.print_list(stickies, ('id', 'name', 'type'))


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<sticky-id>', help='Sticky ID to display')
def do_sticky_show(cl, args):
    sticky = cl.stickies.get(args.lb_id, args.id)
    utils.print_dict(sticky._info)


@utils.arg('--name', metavar='<sticky-name>', required=True,
           help='New sticky name')
@utils.arg('--type', metavar='<type>', required=True,
           help='Type of the sticky')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
def do_sticky_create(cl, args):
    sticky = cl.stickies.create(args.lb_id, args.name, args.type,
                                **extra_args(args.extra))
    utils.print_dict(sticky._info)


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<sticky-id>', help='Sticky ID')
def do_sticky_delete(cl, args):
    cl.stickies.delete(args.lb_id, args.id)


# Virtual IPs


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
def do_vip_list(cl, args):
    vips = cl.vips.list(args.lb_id)
    utils.print_list(vips, ('id', 'name', 'address', 'port'))


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<vip-id>', help='Virtual IP ID to display')
def do_vip_show(cl, args):
    vip = cl.vips.get(args.lb_id, args.id)
    utils.print_dict(vip._info)


@utils.arg('--name', metavar='<vip-name>', required=True,
           help='New VIP name')
@utils.arg('--address', metavar='<vip-address>', required=True,
           help='Virtual IP address')
@utils.arg('--mask', metavar='<vip-mask>', required=True,
           help='Virtual IP address mask')
@utils.arg('--port', metavar='<vip-port>', required=True,
           help='Virtual IP port')
@utils.arg('--type', metavar='<vip-type>', help='Virtual IP type')
@utils.arg('--vlan', metavar='<vip-vlan>', help='Virtual IP VLAN')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
def do_vip_create(cl, args):
    vip = cl.vips.create(args.lb_id, args.name, args.address, args.mask,
                         args.port, type=args.type, vlan=args.vlan,
                         **extra_args(args.extra))
    utils.print_dict(vip._info)


@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('id', metavar='<sticky-id>', help='Sticky ID')
def do_vip_delete(cl, args):
    cl.vips.delete(args.lb_id, args.id)


@utils.arg('--name', metavar='<vip-name>', help='New VIP name')
@utils.arg('--address', metavar='<vip-address>', help='Virtual IP address')
@utils.arg('--mask', metavar='<vip-mask>', help='Virtual IP address mask')
@utils.arg('--port', metavar='<vip-port>', help='Virtual IP port')
@utils.arg('--type', metavar='<vip-type>', help='Virtual IP type')
@utils.arg('--vlan', metavar='<vip-vlan>', help='Virtual IP VLAN')
@utils.arg('lb_id', metavar='<lb-id>', help='LoadBalancer ID')
@utils.arg('--extra', metavar="<key=value>", action='append', default=[],
            help='Extra properties')
def do_vip_update(cl, args):
    kwargs = extra_args(args.extra)
    if args.name:
        kwargs['name'] = args.name
    if args.address:
        kwargs['address'] = args.address
    if args.mask:
        kwargs['mask'] = args.mask
    if args.port:
        kwargs['port'] = args.port
    if args.vlan:
        kwargs['vlan'] = args.vlan

    if not len(kwargs):
        print "Virtual IP not updated, no arguments present."
        return

    try:
        cl.vip.update(args.id, **kwargs)
        print 'Virtual IP has been updated.'
    except Exception, e:
        print 'Unable to update Virtual IP: %s' % e
