from typing import Optional
from ipfabric import IPFClient
from ipfabric.diagrams import (
    IPFDiagram,
    Network,
    NetworkSettings
)


class DataSource:
    def __init__(
        self, server_url, token, snapshot_id, site=None, timeout: Optional[int] = 30
    ):
        if type(site) is str:
            site_filter = {"siteName": ["like", site]}
        elif type(site) is list:
            site_filter = {"siteName": ["reg", "|".join(site)]}

        self.ipf = IPFClient(
            server_url,
            auth=token,
            snapshot_id=snapshot_id,
            verify=False,
            timeout=timeout,
        )

        # Instance Information
        self.system_url = self.ipf.base_url
        self.os_version = self.ipf.os_version
        self.snapshot_id = self.ipf.snapshots[snapshot_id].snapshot_id
        self.snapshot_name = self.ipf.snapshot.name

        # Network data summary
        self.network_devices = self.ipf.inventory.devices.fetch(
            filters=site_filter, columns=["hostname", "fqdn", "domain"]
        )
        self.network_hosts = self.ipf.inventory.hosts.count(filters=site_filter)

        # Network vendors
        self.vendors = self.get_inventory().vendors.all()

        # Interfaces overview
        self.interfaces_count = self.ipf.inventory.interfaces.count(filters=site_filter)
        self.interfaces_switchport = self.ipf.technology.interfaces.switchport.count(
            filters=site_filter
        )
        self.interfaces_channels = (
            self.ipf.technology.port_channels.member_status_table.count(
                filters=site_filter
            )
        )
        self.interfaces_tunnels_ipv4 = (
            self.ipf.technology.interfaces.tunnels_ipv4.count(filters=site_filter)
        )
        self.interfaces_tunnels_ipv6 = (
            self.ipf.technology.interfaces.tunnels_ipv6.count(filters=site_filter)
        )
        self.ipsec_gateways = self.ipf.technology.security.ipsec_gateways.count(
            filters=site_filter
        )
        self.ipsec_tunnels = self.ipf.technology.security.ipsec_tunnels.count(
            filters=site_filter
        )

        # Interfaces Intents
        temp_filter = site_filter.copy()
        temp_filter["duplex"] = ["color", "eq", "20"]
        self.interfaces_duplex = self.ipf.inventory.interfaces.fetch(
            filters=temp_filter,
            columns=["hostname", "intName", "speed", "duplex", "dscr"],
            reports="/inventory/interfaces",
        )
        # Addressing overview
        self.managed_networks = self.ipf.technology.managed_networks.networks.count(
            filters=site_filter
        )
        self.ipv4_interfaces_list = (
            self.ipf.technology.addressing.managed_ip_ipv4.fetch(
                filters=site_filter,
                columns=[
                    "hostname",
                    "intName",
                    "stateL1",
                    "stateL2",
                    "ip",
                    "net",
                    "type",
                    "vrf",
                ],
            )
        )
        self.ipv4_interfaces = len(self.ipv4_interfaces_list)
        self.ipv6_interfaces = self.ipf.technology.addressing.managed_ip_ipv6.count(
            filters=site_filter
        )
        self.arp = self.ipf.technology.addressing.arp_table.count(filters=site_filter)

        # Switching overview
        self.mac = self.ipf.technology.addressing.mac_table.count(filters=site_filter)
        self.vlans = self.ipf.technology.vlans.network_summary.count()
        self.stp_vlans = self.ipf.technology.stp.vlans.count(filters=site_filter)
        self.stp_bridges = self.ipf.technology.stp.bridges.count(filters=site_filter)
        self.stp_virtual_ports = self.ipf.technology.stp.ports.count(
            filters=site_filter
        )
        self.stp_instances = self.ipf.technology.stp.instances.count(
            filters=site_filter
        )
        self.stp_neighbors = self.ipf.technology.stp.neighbors.count(
            filters=site_filter
        )

        # Routing overview
        temp_filter = site_filter.copy()
        self.routes_ipv4 = self.ipf.technology.routing.routes_ipv4.count(
            filters=site_filter
        )
        self.routes_ipv6 = self.ipf.technology.routing.routes_ipv6.count(
            filters=site_filter
        )

        temp_filter["protocol"] = ["eq", "A"]
        self.routes_attached = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "B"]
        self.routes_bgp = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "C"]
        self.routes_connected = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "DGW"]
        self.routes_dgw = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "D"]
        self.routes_eigrp = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "IS-IS"]
        self.routes_isis = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "O"]
        self.routes_ospf = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "R"]
        self.routes_rip = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        temp_filter["protocol"] = ["eq", "S"]
        self.routes_static = self.ipf.technology.routing.routes_ipv4.count(
            filters=temp_filter
        )
        self.routes_multicast = self.ipf.technology.multicast.mroute_table.count(
            filters=site_filter
        )

        # Wireless overview
        self.wireless_controllers = self.ipf.technology.wireless.controllers.count(
            filters=site_filter
        )
        self.wireless_access_points = self.ipf.technology.wireless.access_points.count(
            filters=site_filter
        )
        self.wireless_radios_ssid_summary = (
            self.ipf.technology.wireless.radios_detail.count(filters=site_filter)
        )
        self.wireless_clients = self.ipf.technology.wireless.clients.count(
            filters=site_filter
        )

    def get_inventory(self):
        return self.ipf.inventory

    def get_vendors(self):
        return self.get_inventory().vendors.all()


class Topology:
    def __init__(
        self, server_url, token, params, snapshot_id, timeout: Optional[int] = 30
    ):
        self.ipf = IPFDiagram(
            base_url=server_url,
            auth=token,
            snapshot_id=snapshot_id,
            verify=False,
            timeout=timeout,
        )
        net = Network(sites=params.get("siteName", ""), all_network=False)
        settings = NetworkSettings()
        settings.ungroup_group("Layer 3")
        self.response_svg = self.ipf.diagram_svg(net, graph_settings=settings)

    # def __init__(self, server_url, token, params, snapshot_id):
    #     def get_api_version(api_version_url: str, api_version_token: str) -> dict:
    #         url = f"{api_version_url}/api/version"
    #         headers = {
    #             'Accept': 'application/json',
    #             'X-API-Token': api_version_token
    #         }

    #         response = requests.request("GET", url, headers=headers, verify=False)

    #         return response.json()

    #     api_version = get_api_version(server_url, token)
    #     self.url = f"{server_url}/api/{api_version['apiVersion']}/graphs/"
    #     self.url_svg = f"{server_url}/api/{api_version['apiVersion']}/graphs/svg"
    #     self.headers = {
    #       'X-API-Token': token,
    #       'Content-Type': 'application/json'
    #     }
    #     self.payload = json.dumps({
    #         "parameters": {
    #             "groupBy": "siteName",
    #             "paths": params.get("siteName", ""),
    #             "technologies": {
    #                 "expandDeviceGroups": [],
    #                 "stpInstances": {
    #                     "isolate": False,
    #                     "instances": []
    #                 }
    #             },
    #             "type": "topology"
    #         },
    #         "snapshot": params.get('Snapshot ID', snapshot_id)
    #     })

    #     # self.response = requests.request("POST", self.url, headers=self.headers, data=self.payload, verify=False)
    #     self.response_svg = requests.request("POST", self.url_svg, headers=self.headers, data=self.payload, verify=False)
