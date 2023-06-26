# Desc: Module for generating topology result
import base64

# Importing PathSimulation class from src.data_source
from src.data_source import PathSimulation, Topology


def transform_topology_result(
    server_url_in: str,
    token_in: str,
    topology_params_in: list,
    snapshot_id: str,
    timeout=30,
) -> list:
    """Generates list of JSONs - Topology results"""

    def topology_result(input_params: dict) -> dict:
        """Generates list of JSONs - topology results"""
        topology_response = Topology(
            server_url=server_url_in,
            token=token_in,
            params=input_params,
            snapshot_id=snapshot_id,
            timeout=timeout,
        )
        encoded_svg_data = base64.b64encode(topology_response.response_svg).decode(
            "utf-8"
        )
        return {"svg": f"data:image/svg+xml;base64,{encoded_svg_data}"}

    topology_results_list = []
    for topology_params in topology_params_in:
        topology_results_list.append(
            {"data": topology_params, "result": topology_result(topology_params)}
        )
    return topology_results_list
