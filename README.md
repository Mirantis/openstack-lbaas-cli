# CLI client for OpenStack LBaaS project

* Project wiki: https://github.com/Mirantis/openstack-lbaas-cli/wiki
* OpenStack LBaaS project: https://github.com/Mirantis/openstack-lbaas
* OpenStack Horizon for LBaaS project: https://github.com/Mirantis/openstack-lbaas-horizon/tree/lbaas

### LBaaS overview
* Project overview: https://docs.google.com/document/pub?id=1DRgQhZJ73EyzQ2KvzVQd7Li9YEL7fXWBp8reMdAEhiM
* Screencast: http://www.youtube.com/watch?v=NgAL-kfdbtE
* API draft: https://docs.google.com/document/pub?id=11WWy7MQN1RIK7XdvQtUwkC_EIrykEDproFy9Pekm3wI
* Roadmap: https://docs.google.com/document/pub?id=1yJZXI0WfpAZKhHaLQu7LaxGLrs4REmn0a5bYVbvsCTQ


## Getting Started

If you'd like to run trunk, you can clone the git repo:

```bash
git clone git://github.com/Mirantis/openstack-lbaas-cli.git
```

Install LBaaS.cli by executing:

```bash
./run_tests.sh                           # create virtualenv in .venv folder and run unit tests
.venv/bin/python setup.py install        # install client into virtualenv
```

The client depends on [LBaaS service](https://github.com/Mirantis/openstack-lbaas), start it by executing (refer to project docs for more details):

```bash
cd openstack-lbaas/
./.venv/bin/python ./bin/balancer-api --config-file etc/balancer-api-paste.ini --debug
```

Run LBaaS.cli by executing:

```
.venv/bin/balancer
```


## Features

The tool provides cli interface to LBaaS service.

```
usage: balancer [--os_username <auth-user-name>]
                [--os_password <auth-password>]
                [--os_tenant_name <auth-tenant-name>]
                [--os_tenant_id <tenant-id>] [--os_auth_url <auth-url>]
                [--os_region_name <region-name>]
                [--os_balancer_api_version <balancer-api-version>]
                [--token <service-token>] [--endpoint <service-endpoint>]
                [--endpoint_type <service-endpoint-type>]
                <subcommand> ...

Command-line interface to the OpenStack LBaaS API.

Positional arguments:
  <subcommand>
    algorithms-list     List available algorithms
    device-create       Create a new load-balancing device
    device-delete       Delete a specific load-balancing device
    device-list         List available load-balancing devices
    device-show         Describe a specific load-balancing device
    lb-create           Create a new load balancer
    lb-delete           Delete a specific load balancer
    lb-list             List load balancers for a particular device
    lb-show             Describe a specific load balancer
    lb-update           Update a specific load balancer
    node-create         Create a new node
    node-delete         Delete a specific node
    node-list           List nodes for a particular load balancer
    node-show           Describe a specific node
    node-update         Update a specific node
    probe-create        Create a new probe
    probe-delete        Delete a specific probe
    probe-list          List probes for a particular load balancer
    probe-show          Describe a specific probe
    protocols-list      List available protocols
    sticky-create       Create a new sticky command
    sticky-delete       Delete a specific sticky command
    sticky-list         List sticky commands for a particular load balancer
    sticky-show         Describe a specific sticky command
    vip-create          Create a new virtual IP
    vip-delete          Delete a specific virtual IP
    vip-list            List virtual IPs for a particular load balancer
    vip-show            Describe a specific virtual IP
    vip-update          Update a specific virtual IP
    help                Display help about this program or one of its
                        subcommands.

Optional arguments:
  --os_username <auth-user-name>
                        Defaults to env[OS_USERNAME]
  --os_password <auth-password>
                        Defaults to env[OS_PASSWORD]
  --os_tenant_name <auth-tenant-name>
                        Defaults to env[OS_TENANT_NAME]
  --os_tenant_id <tenant-id>
                        Defaults to env[OS_TENANT_ID]
  --os_auth_url <auth-url>
                        Defaults to env[OS_AUTH_URL]
  --os_region_name <region-name>
                        Defaults to env[OS_REGION_NAME]
  --os_balancer_api_version <balancer-api-version>
                        Defaults to env[OS_BALANCER_API_VERSION] or 2.0
  --token <service-token>
                        Defaults to env[SERVICE_TOKEN]
  --endpoint <service-endpoint>
                        Defaults to env[SERVICE_ENDPOINT]
  --endpoint_type <service-endpoint-type>
                        Defaults to env[OS_BALANCER_ENDPOINT_TYPE]

See "balancer help COMMAND" for help on a specific command.
```

## Example of typical workflow

Before running the tool make sure that LBaaS service is up and running. In the
following examples it is assumed that service is available at localhost:8181.

### 1. Create a new device

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181 device-create --name test --type HAPROXY --version 1 --ip 192.168.19.245 --port 22 --user user --password swordfish

   +----------+----------------------------------+
   | Property | Value                            |
   +----------+----------------------------------+
   | id       | 46ae427db95e464bb99ae0b883c627cc |
   | ip       | 192.168.19.245                   |
   | name     | test                             |
   | password | swordfish                        |
   | port     | 22                               |
   | type     | HAPROXY                          |
   | user     | user                             |
   | version  | 1                                |
   +----------+----------------------------------+
```

### 2. Show list of devices

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181 device-list

   +----------------------------------+------+---------+---------+----------------+------+------+-----------+
   | id                               | name | type    | version | ip             | port | user | password  |
   +----------------------------------+------+---------+---------+----------------+------+------+-----------+
   | 46ae427db95e464bb99ae0b883c627cc | test | HAPROXY | 1       | 192.168.19.245 | 22   | user | swordfish |
   +----------------------------------+------+---------+---------+----------------+------+------+-----------+
```

### 3. Create a new load balancer

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181/tenant_id lb-create --name test-lb --algorithm ROUND_ROBIN --protocol HTTP

   +------------+----------------------------------+
   | Property   | Value                            |
   +------------+----------------------------------+
   | algorithm  | RoundRobin                       |
   | created_at | 2012-09-12T15:38:26.425493       |
   | deployed   | True                             |
   | device_id  | c0ef8a3b7cad4dcbbe2739302a35a67d |
   | id         | 1158c2575d2b408991fe142c8b70f77e |
   | name       | test-lb                          |
   | protocol   | HTTP                             |
   | status     | ACTIVE                           |
   | tenant_id  | tenant_id                        |
   | updated_at | 2012-09-12T15:38:42.094760       |
   +------------+----------------------------------+
```

### 4. Create virtual ip

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181/tenant_id vip-create --name test-vip --address 192.168.19.245 --mask 255.255.255.255 --port 80  1158c2575d2b408991fe142c8b70f77e

   +----------+----------------------------------+
   | Property | Value                            |
   +----------+----------------------------------+
   | address  | 192.168.19.245                   |
   | deployed | None                             |
   | id       | 2db07baed6ec4608bb263d546c40603e |
   | lb_id    | 1158c2575d2b408991fe142c8b70f77e |
   | mask     | 255.255.255.255                  |
   | name     | test-vip                         |
   | port     | 80                               |
   | protocol | HTTP                             |
   | sf_id    | 8684b200edb24ec1970b4280b16fd466 |
   | status   | None                             |
   +----------+----------------------------------+
```
_Note_ The load balancer id should be changed to the one returned by lb-create

### 5. Add node to load balancer

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181/tenant_id node-create --name node-uno --type dummy --address 192.168.19.245 --port 8001 --weight 1 --condition ENABLED  1158c2575d2b408991fe142c8b70f77e

   +-----------+----------------------------------+
   | Property  | Value                            |
   +-----------+----------------------------------+
   | address   | 192.168.19.245                   |
   | condition | ENABLED                          |
   | deployed  | True                             |
   | id        | 033c488b66204b35a87e6d38701a42cc |
   | name      | node-uno                         |
   | parent_id | None                             |
   | port      | 8001                             |
   | sf_id     | 8684b200edb24ec1970b4280b16fd466 |
   | status    | INSERVICE                        |
   | type      | dummy                            |
   | vm_id     | None                             |
   | weight    | 1                                |
   +-----------+----------------------------------+
```
_Note_ The load balancer id should be changed to the one returned by lb-create

### 6. Specify probe for node health monitoring

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181/tenant_id probe-create --name test-probe --type HTTP --extra url=/ --extra method=GET --extra status=200  1158c2575d2b408991fe142c8b70f77e

   +----------+----------------------------------+
   | Property | Value                            |
   +----------+----------------------------------+
   | deployed | None                             |
   | id       | eede6d59863c4a4bae1f6800233d7c98 |
   | method   | GET                              |
   | name     | test-probe                       |
   | sf_id    | 8684b200edb24ec1970b4280b16fd466 |
   | status   | 200                              |
   | type     | HTTP                             |
   | url      | /                                |
   +----------+----------------------------------+
```
_Note_ The load balancer id should be changed to the one returned by lb-create

### 7. Suspend node

```
   # .venv/bin/balancer --token fake --endpoint http://localhost:8181/tenant_id node-update --condition DISABLED  1158c2575d2b408991fe142c8b70f77e 033c488b66204b35a87e6d38701a42cc

   Node has been updated.
   +-----------+----------------------------------+
   | Property  | Value                            |
   +-----------+----------------------------------+
   | address   | 192.168.19.245                   |
   | condition | DISABLED                         |
   | deployed  | True                             |
   | id        | 033c488b66204b35a87e6d38701a42cc |
   | name      | node-uno                         |
   | parent_id | None                             |
   | port      | 8001                             |
   | sf_id     | 8684b200edb24ec1970b4280b16fd466 |
   | status    | INSERVICE                        |
   | type      | dummy                            |
   | vm_id     | None                             |
   | weight    | 1                                |
   +-----------+----------------------------------+
```
_Note_ The load balancer id and node id should be changed to the one returned by lb-create and node-create
