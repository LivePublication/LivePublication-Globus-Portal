"""
This file contains a single LivePublication Action Provider flow using Gladier & Globus interfaces. 
It serves as an experimental testbench for the LivePublication CLI.
"""
import os, sys

current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

from gladier import GladierBaseClient, generate_flow_definition
# Import config variables & custom tools
from livepublication_portal.flows.ListDirectory.local_config import ComputeUUID
from livepublication_portal.flows.ListDirectory.flow_components.ls import FileSystemListCommand
from livepublication_portal.flows.utils import update_flows_json, FlowInfo


@staticmethod
@generate_flow_definition
class Example_Flow(GladierBaseClient):
    """
    Note the order of the tools - this defines the order of the flow.
    Also, note how this comment is included within the WEP as a comment.

    These components (here called tools) are disconnected descriptions of the 
    actions which gladier will stitch together into a flow.
    When instantiating the prospective provenance, these components could be
    used as the software components of each action.
    """
    gladier_tools = [
        FileSystemListCommand,
    ]

    globus_group = "9e155e5c-e011-11ee-a4a3-8fbdadf65a0b"

flow_input = {
    "input": {
        "compute_endpoint": ComputeUUID
    }
}



if __name__ == "__main__":
    ls_client = Example_Flow()
    ls_client.sync_flow()
    fid = ls_client.get_flow_id() 
    flow = ls_client.run_flow(flow_input=flow_input)
    compute_function_ids = ls_client.get_compute_function_ids()
    if compute_function_ids:
        print(f"Compute functions embeeded in this flow: {compute_function_ids}")
    url = f"https://app.globus.org/flows/{fid}"
    print(f"You can view the flow from the Globus Webapp here: {url}")

    """
    Define the flow information for this flow. 
    This is used to populate the flow information cards in 
    the control-centre. 
    Note: clear the flows.json file when re-configuring with this script
    """
    flow_info = FlowInfo(
        title='List Directory Flow',
        name="ls-flow",
        author='Augustus Ellerm',
        class_name='Example',
        uuid=fid,
        url=url,
        description='Returns the working directory of the globus-compute node.',
        start_url='ls-compute/',  # You will need to define a URL for starting the flow in your Django app
        compute_function_ids=compute_function_ids
    )

    update_flows_json(flow_info)