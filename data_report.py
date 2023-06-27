# Import the required modules
import os
from datetime import datetime
from pathlib import Path

from ipdb import set_trace as debug
from jinja2 import Environment, FileSystemLoader
from src.data_source import DataSource
from src.modules import transform_topology_result
from weasyprint import HTML


def check_file_exists(file: Path):
    if os.path.exists(file):
        print(f"File created successfully at `{file}`")
    else:
        print(f"Error: File `{file}` creation failed")


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
        user_input = input(
            "Enter a siteName or a list of siteName separated by commas: "
        )
        values = user_input.split(",")
        # If the user entered only one value, remove leading/trailing white space
        if len(values) == 1:
            value = values[0].strip()
            if isinstance(value, str) and value != "":
                print(f"You entered a string: {value}")
                return value
            else:
                print("Empty input.")
        elif all(isinstance(val.strip(), str) for val in values):
            print(f"You entered a list of strings: {values}")
            return [val.strip() for val in values]
        else:
            print(
                "Invalid input. Please enter a string or a list of strings separated by commas."
            )


def main():
    # Ask for the list of sites to generate the report for
    input_site = input_validation()
    # Initialize DataSources with a token and server_url
    server_url = os.environ.get("IPF_URL")
    token = os.environ.get("IPF_TOKEN")
    snapshot_id = "$last"
    ipf_timeout = 15
    data_source = DataSource(
        server_url=server_url,
        token=token,
        snapshot_id=snapshot_id,
        site=input_site,
        timeout=ipf_timeout,
    )

    # The time part
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H-%M")

    # HTML, PDF and CSS file paths
    os.makedirs("export", exist_ok=True)
    html_file_path = Path(f"export/IPF-Report-{formatted_time}.html")
    pdf_file_path = Path(f"export/IPF-Report-{formatted_time}.pdf")
    css_file_path = Path("src/style.css")

    # Set up the Jinja2 environment and load the HTML template
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("src/template.html")

    # Diagrams based on siteName
    topology_list = [
        {
            "Name": input_site,
            "groupBy": "siteName",
            "siteName": [input_site] if type(input_site) is str else input_site,
        }
    ]

    # Prepare the context data to be inserted into the HTML template
    context = {
        # Site(s)
        "site": input_site,
        # Time
        "formatted_time": formatted_time,
        # Instance Information
        "system_url": data_source.system_url,
        "os_version": data_source.os_version,
        "snapshot_id": data_source.snapshot_id,
        "snapshot_name": data_source.snapshot_name,
        # Network data summary
        "network_devices": data_source.network_devices,
        "network_hosts": data_source.network_hosts,
        # Interfaces overview
        "interfaces_count": data_source.interfaces_count,
        "interfaces_switchport": data_source.interfaces_switchport,
        "interfaces_channels": data_source.interfaces_channels,
        "interfaces_tunnels_ipv4": data_source.interfaces_tunnels_ipv4,
        "interfaces_tunnels_ipv6": data_source.interfaces_tunnels_ipv6,
        "ipsec_gateways": data_source.ipsec_gateways,
        "ipsec_tunnels": data_source.ipsec_tunnels,
        # Interfaces Intent
        "interfaces_duplex": data_source.interfaces_duplex,
        # Addressing overview
        "managed_networks": data_source.managed_networks,
        "ipv4_interfaces_list": data_source.ipv4_interfaces_list,
        "ipv4_interfaces": data_source.ipv4_interfaces,
        "ipv6_interfaces": data_source.ipv6_interfaces,
        "arp": data_source.arp,
        # Switching overview
        "stp_bridges": data_source.stp_bridges,
        "stp_instances": data_source.stp_instances,
        "stp_neighbors": data_source.stp_neighbors,
        "stp_virtual_ports": data_source.stp_virtual_ports,
        "stp_vlans": data_source.stp_vlans,
        "vlans": data_source.vlans,
        "mac": data_source.mac,
        # Routing overview
        "routes_ipv4": data_source.routes_ipv4,
        "routes_ipv6": data_source.routes_ipv6,
        "routes_multicast": data_source.routes_multicast,
        "routes_attached": data_source.routes_attached,
        "routes_connected": data_source.routes_connected,
        "routes_dgw": data_source.routes_dgw,
        "routes_static": data_source.routes_static,
        "routes_bgp": data_source.routes_bgp,
        "routes_ospf": data_source.routes_ospf,
        "routes_isis": data_source.routes_isis,
        "routes_eigrp": data_source.routes_eigrp,
        "routes_rip": data_source.routes_rip,
        # Wireless overview
        "wireless_controllers": data_source.wireless_controllers,
        "wireless_access_points": data_source.wireless_access_points,
        "wireless_radios_ssid_summary": data_source.wireless_radios_ssid_summary,
        "wireless_clients": data_source.wireless_clients,
        # Topology
        "topology_context": transform_topology_result(
            server_url_in=server_url,
            token_in=token,
            topology_params_in=topology_list,
            snapshot_id=snapshot_id,
            timeout=ipf_timeout,
        )
        if topology_list
        else "",
    }
    # set_trace()
    # Save rendered HTML to a file
    with open(html_file_path, "w") as f:
        f.write(template.render(context))
    # Save rendered PDF to a file
    HTML(html_file_path).write_pdf(pdf_file_path, stylesheets=[css_file_path])
    # check if file exists and print confirmation message
    check_file_exists(html_file_path)
    check_file_exists(pdf_file_path)


if __name__ == "__main__":
    main()
