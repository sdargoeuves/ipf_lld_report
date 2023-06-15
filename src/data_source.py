import json
import requests
from ipfabric import IPFClient


class DataSource:
    def __init__(self, server_url, token, snapshot_id, site=None):
        site_filter = {} if site is None else {"siteName": ["like", site]}
        self.ipf = IPFClient(server_url, auth=token, snapshot_id=snapshot_id, verify=False, timeout=15)

        # Instance Information
        self.system_url = self.ipf.base_url
        self.os_version = self.ipf.os_version
        self.snapshot_id = self.ipf.snapshots[snapshot_id].snapshot_id
        self.snapshot_name = self.ipf.snapshot.name
        
        # Network data summary
        print(site_filter)
        self.network_devices = self.ipf.inventory.devices.fetch(filters=site_filter, columns=["hostname", "fqdn", "domain"])
        self.network_hosts = self.ipf.inventory.hosts.count(filters=site_filter)

        # Network vendors
        self.vendors = self.get_inventory().vendors.all()

        # Interfaces overview
        self.interfaces_active = self.ipf.snapshot.interface_active_count
        self.interfaces_edge = self.ipf.snapshot.interface_edge_count
        self.interfaces_switchport = self.ipf.technology.interfaces.switchport.count()

        self.interfaces_channels = self.ipf.technology.port_channels.member_status_table.count()
        self.interfaces_tunnels_ipv4 = self.ipf.technology.interfaces.tunnels_ipv4.count()
        self.interfaces_tunnels_ipv6 = self.ipf.technology.interfaces.tunnels_ipv6.count()
        self.ipsec_gateways = self.ipf.technology.security.ipsec_gateways.count()
        self.ipsec_tunnels = self.ipf.technology.security.ipsec_tunnels.count()

        # Addressing overview
        self.managed_networks = self.ipf.technology.managed_networks.networks.count()
        self.ipv4_interfaces = self.ipf.technology.addressing.managed_ip_ipv4.count()
        self.ipv6_interfaces = self.ipf.technology.addressing.managed_ip_ipv6.count()
        self.arp = self.ipf.technology.addressing.arp_table.count()
        self.vrfs = self.ipf.technology.routing.vrf_summary.count()

        # Switching overview
        self.mac = self.ipf.technology.addressing.mac_table.count()
        self.vlans = self.ipf.technology.vlans.network_summary.count()
        self.stp_vlans = self.ipf.technology.stp.vlans.count()
        self.stp_bridges = self.ipf.technology.stp.bridges.count()
        self.stp_virtual_ports = self.ipf.technology.stp.ports.count()
        self.stp_instances = self.ipf.technology.stp.instances.count()
        self.stp_neighbors = self.ipf.technology.stp.neighbors.count()

        # Routing overview
        self.routes_ipv4 = self.ipf.technology.routing.routes_ipv4.count()
        self.routes_ipv6 = self.ipf.technology.routing.routes_ipv6.count()
        self.routes_attached = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "A"]})
        self.routes_bgp = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "B"]})
        self.routes_connected = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "C"]})
        self.routes_eigrp = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "D"]})
        self.routes_isis = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "IS-IS"]})
        self.routes_ospf = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["like", "O"]})
        self.routes_rip = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "R"]})
        self.routes_static = self.ipf.technology.routing.routes_ipv4.count(filters={"protocol": ["eq", "S"]})
        self.routes_multicast = self.ipf.technology.multicast.mroute_table.count()

        # Wireless overview
        self.stp_bridges = self.ipf.technology.wireless.controllers.count()
        self.stp_virtual_ports = self.ipf.technology.wireless.access_points.count()
        self.stp_instances = self.ipf.technology.wireless.radios_ssid_summary.count()
        self.stp_neighbors = self.ipf.technology.wireless.clients.count()

    def get_inventory(self):
        return self.ipf.inventory

    def get_vendors(self):
        return self.get_inventory().vendors.all()


class PathSimulation:
    def __init__(self, server_url, token, params):
        def get_api_version(api_version_url: str, api_version_token: str) -> dict:
            url = f"{api_version_url}/api/version"
            headers = {
                'Accept': 'application/json',
                'X-API-Token': api_version_token
            }

            response = requests.request("GET", url, headers=headers, verify=False)

            return response.json()

        api_version = get_api_version(server_url, token)
        self.url = f"{server_url}/api/{api_version['apiVersion']}/graphs/"
        self.url_svg = f"{server_url}/api/{api_version['apiVersion']}/graphs/svg"
        self.headers = {
          'X-API-Token': token,
          'Content-Type': 'application/json'
        }
        self.payload = json.dumps({
            "parameters": {
                "destinationPoint": params.get('Destination IP', ''),
                "groupBy": "siteName",
                "networkMode": False,
                "pathLookupType": "unicast",
                "securedPath": True,
                "startingPoint": params.get('Source IP', ''),
                "type": "pathLookup",
                "firstHopAlgorithm": {
                    "type": "automatic"
                },
                "dstRegions": ".*",
                "enableRegions": False,
                "fragmentOffset": 0,
                "otherOptions": {
                    "applications": "",
                    "tracked": False
                },
                "protocol": params.get('Protocol', 'tcp'),
                "srcRegions": ".*",
                "ttl": params.get('TTL', 64),
                "l4Options": {
                    "dstPorts": params.get('Destination port', '80'),
                    "srcPorts": params.get('Source port', '1024-65535'),
                    "flags": []
                }
            },
            "snapshot": params.get('Snapshot ID', '$last')
        })

        # self.response = requests.request("POST", self.url, headers=self.headers, data=self.payload, verify=False)
        self.response_svg = requests.request("POST", self.url_svg, headers=self.headers, data=self.payload, verify=False)


class Topology:
    def __init__(self, server_url, token, params, snapshot_id):
        def get_api_version(api_version_url: str, api_version_token: str) -> dict:
            url = f"{api_version_url}/api/version"
            headers = {
                'Accept': 'application/json',
                'X-API-Token': api_version_token
            }

            response = requests.request("GET", url, headers=headers, verify=False)

            return response.json()

        api_version = get_api_version(server_url, token)
        self.url = f"{server_url}/api/{api_version['apiVersion']}/graphs/"
        self.url_svg = f"{server_url}/api/{api_version['apiVersion']}/graphs/svg"
        self.headers = {
          'X-API-Token': token,
          'Content-Type': 'application/json'
        }
        self.payload = json.dumps({
            "parameters": {
                "groupBy": "siteName",
                "paths": params.get("siteName", ""),
                "technologies": {
                    "expandDeviceGroups": [],
                    "stpInstances": {
                        "isolate": False,
                        "instances": []
                    }
                },
                "type": "topology"
            },
            "snapshot": params.get('Snapshot ID', snapshot_id)
        })

        # self.response = requests.request("POST", self.url, headers=self.headers, data=self.payload, verify=False)
        self.response_svg = requests.request("POST", self.url_svg, headers=self.headers, data=self.payload, verify=False)

