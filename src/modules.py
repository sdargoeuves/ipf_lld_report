# Desc: Module for generating path simulation results

import base64
# Importing PathSimulation class from src.data_source
from src.data_source import PathSimulation, Topology


def transform_path_result(server_url_in: str, token_in: str, path_params_in: list) -> list:
    """ Generates list of JSONs - path simulation results"""
    def path_result(input_params: dict) -> dict:
        """ Generates list of JSONs - path simulation results"""
        path_response = PathSimulation(server_url_in, token_in, input_params)
        encoded_svg_data = base64.b64encode(path_response.response_svg.text.encode('utf-8')).decode('utf-8')
        return {'svg': f"data:image/svg+xml;base64,{encoded_svg_data}"}

    path_results_list = []
    for path_params in path_params_in:
        path_results_list.append({
            'data': path_params,
            'result': path_result(path_params)
        })
    return path_results_list

def transform_topology_result(server_url_in: str, token_in: str, topology_params_in: list, snapshot_id: str) -> list:
    """ Generates list of JSONs - path simulation results"""
    def topology_result(input_params: dict) -> dict:
        """ Generates list of JSONs - topology results"""
        topology_response = Topology(server_url_in, token_in, input_params, snapshot_id)
        encoded_svg_data = base64.b64encode(topology_response.response_svg.text.encode('utf-8')).decode('utf-8')
        return {'svg': f"data:image/svg+xml;base64,{encoded_svg_data}"}

    topology_results_list = []
    for topology_params in topology_params_in:
        topology_results_list.append({
            'data': topology_params,
            'result': topology_result(topology_params)
        })
    return topology_results_list