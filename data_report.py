# Import the required modules
from src.modules import transform_path_result, transform_topology_result
from src.data_source import DataSource

from ipdb import set_trace
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
from weasyprint import HTML

def input_validation():
    """
    This function prompts the user to enter a string or a list of strings separated by commas, and validates the input.
    If the input is a single string, it is returned with leading and trailing white space removed.
    If the input is a list of strings, the list is returned.
    If the input is invalid, the function prints an error message and prompts the user again.

    Returns:
    - str: if the user entered a single string
    - list of str: if the user entered a list of strings
    """
    while True:
        user_input = input("Enter a string or a list of strings separated by commas: ")
        values = user_input.split(",")

        # If the user entered only one value, remove leading/trailing white space
        if len(values) == 1:
            value = values[0].strip()
            if isinstance(value, str):
                print(f"You entered a string: {value}")
                return value
        elif all(isinstance(val.strip(), str) for val in values):
            print(f"You entered a list of strings: {values}")
            return value
        print("Invalid input. Please enter a string or a list of strings separated by commas.")

def main():
    #Ask for the list of sites to generate the report for
    input_site = input_validation()
    # Initialize DataSources with a token and server_url
    server_url = os.environ.get('IPF_URL')  # netsim
    token = os.environ.get('IPF_TOKEN')  # netsim

    snapshot_id = "$last"
    data_source = DataSource(server_url, token, snapshot_id, input_site)

    # The time part
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H-%M")

    # HTML, PDF and CSS file paths
    html_file_path = Path(f"export/IPF-Report-{formatted_time}.html")
    pdf_file_path = Path(f"export/IPF-Report-{formatted_time}.pdf")
    css_file_path = Path('src/style.css')

    # Set up the Jinja2 environment and load the HTML template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('src/template.html')

    # Diagrams based on siteName
    topology_list = [
        {
            "Name": input_site,
            "groupBy": "siteName",
            "siteName": [input_site]
        }
    ]

    # Prepare the context data to be inserted into the HTML template
    context = {

        # Time
        'formatted_time': formatted_time,

        # Instance Information
        'system_url': data_source.system_url,
        'os_version': data_source.os_version,
        'snapshot_id': data_source.snapshot_id,
        'snapshot_name': data_source.snapshot_name,
        # Network data summary
        'network_devices': data_source.network_devices,
        'network_hosts': data_source.network_hosts,

        # Network vendors
        'vendors': data_source.get_vendors(),

        # Interfaces overview
        'interfaces_active': data_source.interfaces_active,
        'interfaces_edge': data_source.interfaces_edge,
        'interfaces_switchport': data_source.interfaces_switchport,
        'interfaces_channels': data_source.interfaces_channels,
        'interfaces_tunnels_ipv4': data_source.interfaces_tunnels_ipv4,
        'interfaces_tunnels_ipv6': data_source.interfaces_tunnels_ipv6,
        'ipsec_gateways': data_source.ipsec_gateways,
        'ipsec_tunnels': data_source.ipsec_tunnels,

        # Addressing overview
        'managed_networks': data_source.managed_networks,
        'ipv4_interfaces': data_source.ipv4_interfaces,
        'ipv6_interfaces': data_source.ipv6_interfaces,
        'arp': data_source.arp,
        'vrfs': data_source.vrfs,

        # Switching overview
        'stp_bridges': data_source.stp_bridges,
        'stp_instances': data_source.stp_instances,
        'stp_neighbors': data_source.stp_neighbors,
        'stp_virtual_ports': data_source.stp_virtual_ports,
        'stp_vlans': data_source.stp_vlans,
        'vlans': data_source.vlans,
        'mac': data_source.mac,

        # Routing overview
        'routes_ipv4': data_source.routes_ipv4,
        'routes_ipv6': data_source.routes_ipv6,
        'routes_multicast': data_source.routes_multicast,
        'routes_attached': data_source.routes_attached,
        'routes_connected': data_source.routes_connected,
        'routes_static': data_source.routes_static,
        'routes_bgp': data_source.routes_bgp,
        'routes_ospf': data_source.routes_ospf,
        'routes_isis': data_source.routes_isis,
        'routes_eigrp': data_source.routes_eigrp,
        'routes_rip': data_source.routes_rip,

        # Wireless overview
        'wireless_controllers': data_source.stp_bridges,
        'wireless_access_points': data_source.stp_virtual_ports,
        'wireless_radios_ssid_summary': data_source.stp_instances,
        'wireless_clients': data_source.stp_neighbors,

        # Topology
        'topology_context': transform_topology_result(server_url, token, topology_list, snapshot_id) if topology_list else ""
    }
    # set_trace()
    # Save rendered HTML to a file
    with open(html_file_path, 'w') as f:
        f.write(template.render(context))

    # Save rendered PDF to a file
    HTML(html_file_path).write_pdf(
        pdf_file_path,
        stylesheets=[css_file_path]
    )


if __name__ == "__main__":
    main()
