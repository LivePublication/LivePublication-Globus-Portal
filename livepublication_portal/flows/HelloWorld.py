"""
Make sure you are part of the Globus Flows Users group so that you can deploy this flow,
or delete any prior flows before running this example.

Make sure also to install Gladier (pip install gladier)
"""
import json
from gladier import GladierBaseClient
from pprint import pprint


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
    Note: clear the flows.json file when re-configuring with this script
    """
    flow_info = {
        'title': 'Hello World Flow',
        'name': "hello-flow",
        'author': 'Augustus Ellerm',
        'class': 'Example',
        'uuid': fid,
        'url': url,
        'description': 'An example flow that prints "hello_world" and sleeps for a given time.',
        'start_url': 'hello-world/',  # You will need to define a URL for starting the flow in your Django app
    }

    # Read existing flows and update with new flow information
    flows = []
    try:
        with open('flows/flows.json', 'r') as f:
            for line in f:
                flow = json.loads(line.strip())
                if flow['title'] != flow_info['title']:
                    flows.append(flow)
    except FileNotFoundError:
        pass  # File doesn't exist yet, no need to read

    flows.append(flow_info)

    # Rewrite the flows.json file with updated flow information
    with open('flows/flows.json', 'w') as f:
        for flow in flows:
            json.dump(flow, f)
            f.write('\n')

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
