# IP Fabric Data Report Generator

This Python script generates a health report for a network using data from two data sources (snapshots). It uses IP Fabric's SDK to fetch data and Jinja2 and HTML to create report, which is then exported to PDF. 

## Requirements

* Python 3.7 or higher
* jinja2
* ipfabric
* weasyprint

## Usage

* Clone this repository.
* Install the weasyprint module using pip install weasyprint.
* Set the appropriate values for server_url, token and snapshot_id variables in main.py.
* Run the script using python main.py.
* The generated report will be saved in export folder.

To use this script, you will need to provide the following parameters:

* `token`: Your API token for the IP Fabric server
* `server_url`: The URL of the IP Fabric server
* `snapshot_id`: The first snapshot ID for baseline data collection

## Data Collection

To collect data about your network, simply create an instance of the DataSource class and pass in the required parameters:

```python
from src.data_source import DataSource

server_url = "https://<IP_FABRIC_SERVER>"
token = "<API_TOKEN>"
snapshot_id = "<SNAPSHOT_ID>"

datasource = DataSource(server_url, token, snapshot_id)
```

This will create an instance of the DataSource class and populate its attributes with data about the network configuration.

## Topology

Enter the name of the site you want to create the report for, and the topology will be the default layout for this site.


## Report Contents

The report contains the following sections:

* Network data summary
* Interfaces overview
* Addressing overview
* Switching overview
* Routing overview
* Wireless overview
* Topology

## Improvements

* Add mode data to comparee
* Add CVEs from SDK
