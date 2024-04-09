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
This file contains a single LivePublication flow using Gladier & Globus interfaces. 
"""

from gladier import GladierBaseClient
# Import config variables & custom tools
from livepublication_portal.flows.utils import update_flows_json, FlowInfo

class HelloClient(GladierBaseClient):
    """An example flow that prints 'hello_world' and sleeps for a given time.
    Note the inclusion of globus_group in the client - this grants permissions
    to those in the group (LivePublication in this instance) to re-execute the flow"""
    globus_group = "9e155e5c-e011-11ee-a4a3-8fbdadf65a0b"
    flow_definition = {
        "StartAt": "Hello",
        "States": {
            "Hello": {
                "ActionUrl": "https://actions.globus.org/hello_world",
                "Type": "Action",
                "Parameters": {
                    "echo_string.$": "$.input.echo_string",
                    "sleep_time.$": "$.input.sleep_time",
                },
                "End": True,
            }
        },
    }


if __name__ == "__main__":

    # Instantiate the client
    hello_world_client = HelloClient()
    hello_world_client.sync_flow()
    fid = hello_world_client.get_flow_id()
    url = f"https://app.globus.org/flows/{fid}"
    print(f"Set this flow in your settings.py under FLOW_ID: {fid}")
    print(f"You can view the flow from the Globus Webapp here: {url}")


    """
    Define the flow information for this flow. 
    This is used to populate the flow information cards in 
    the control-centre. 
    """
    compute_function_ids = None # No compute functions in this flow
    flow_info = FlowInfo(
        title='Hello World Flow',
        name="hello-flow",
        author='Augustus Ellerm',
        class_name='Example',
        uuid=fid,
        url=url,
        description='An example flow that prints "hello_world" and sleeps for a given time.',
        start_url='hello-world/',  # You will need to define a URL for starting the flow in your Django app
        compute_function_ids=compute_function_ids
    )
    
    update_flows_json(flow_info)