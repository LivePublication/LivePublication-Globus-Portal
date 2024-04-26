"""
Make sure you are part of the Globus Flows Users group so that you can deploy this flow,
or delete any prior flows before running this example.

Make sure also to install Gladier (pip install gladier)
"""
import os, sys

current_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

"""
This file contains a single LivePublication Action Provider flow using Gladier & Globus interfaces. 
It serves as an experimental testbench for the LivePublication CLI.
"""

from gladier import GladierBaseClient, generate_flow_definition
# Import config variables & custom tools
from livepublication_portal.flows.BeeMovie.local_config import DataStoreUUID, ComputeUUID, Compute_DS_UUID, InputPath, OutputPath, TransferFile
from livepublication_portal.flows.BeeMovie.flow_components.BeeMovieScript import GetBeeMovieScript
from livepublication_portal.flows.BeeMovie.flow_components.ListDirectory import FileSystemListCommand
from livepublication_portal.flows.utils import update_flows_json, FlowInfo


@staticmethod
@generate_flow_definition
class BeeMovieScript(GladierBaseClient):
    """
    Note the order of the tools - this defines the order of the flow.
    Also, note how this comment is included within the WEP as a comment.

    These components (here called tools) are disconnected descriptions of the 
    actions which gladier will stitch together into a flow.
    When instantiating the prospective provenance, these components could be
    used as the software components of each action.
    """
    gladier_tools = [
        "gladier_tools.globus.Transfer:ToCompute",
        FileSystemListCommand,
        GetBeeMovieScript,
        "gladier_tools.globus.Transfer:FromCompute"
    ]

    # LivePublication group access
    globus_group = "9e155e5c-e011-11ee-a4a3-8fbdadf65a0b"

flow_input = {
    "input": {
        # Input vars for transfer 1 (FromSource)
        "to_compute_transfer_source_endpoint_id": DataStoreUUID,
        "to_compute_transfer_destination_endpoint_id": Compute_DS_UUID,
        "to_compute_transfer_source_path": os.path.join(OutputPath, TransferFile),
        "to_compute_transfer_destination_path": os.path.join(InputPath, TransferFile),
        "to_compute_transfer_recursive": False,
        # Input vars for transfer 2 (ToDestination)
        "from_compute_transfer_source_endpoint_id": Compute_DS_UUID,
        "from_compute_transfer_destination_endpoint_id": DataStoreUUID,
        "from_compute_transfer_source_path": os.path.join(OutputPath, TransferFile),
        "from_compute_transfer_destination_path": os.path.join(InputPath, TransferFile),
        "from_compute_transfer_recursive": False,
        # Compute Endpoint for interfacing with the compute endpoint
        "compute_endpoint": ComputeUUID
    }
}


if __name__ == "__main__":
    # Instantiate the client
    BeeMovieScript_client = BeeMovieScript()
    BeeMovieScript_client.sync_flow()
    fid = BeeMovieScript_client.get_flow_id()
    compute_function_ids = BeeMovieScript_client.get_compute_function_ids()
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
        title='Bee Movie Flow',
        name="bee-flow",
        author='Augustus Ellerm',
        class_name='Example',
        uuid=fid,
        url=url,
        description='Transfers an empty text file to compute -> downoads BeeMovie script using compute -> Transfers back to store.',
        start_url='hello-world/',  
        compute_function_ids=compute_function_ids
    )

    update_flows_json(flow_info)

    # # Run the flow and track progress, if you want to test!
    # flow_input = {
    #     "input": {
    #         "echo_string": "hello_world",
    #         "sleep_time": 1
    #     }
    # }
    # flow = hello_world_client.run_flow(flow_input=flow_input, label="Schema Example")
    # run_id = flow["run_id"]
    # hello_world_client.progress(run_id)
    # pprint(hello_world_client.get_status(run_id))
