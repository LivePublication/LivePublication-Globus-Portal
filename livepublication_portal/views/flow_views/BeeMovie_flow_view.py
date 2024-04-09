import logging
import os
import globus_sdk 
import json 

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms
from globus_portal_framework.gclients import load_globus_access_token

log = logging.getLogger(__name__)

class BeeMovieForm(forms.Form):
    """
    This is a Django form to control and validate user input fields.

    https://docs.djangoproject.com/en/4.2/topics/forms/

    Typically this would go into its own forms.py class, but it's added here for simplicity.
    """

    label = forms.CharField(
        initial="An exmaple flow",
        max_length=256,
        help_text="A nice label to add context to this flow",
    )

    tags = forms.CharField(
        label="Tags",
        max_length=256,
        help_text="Tags help categorize many runs over time. You can use a comma separated list here.",
    )

    # Input vars for transfer 1 (FromSource)
    to_compute_transfer_source_endpoint_id = forms.CharField(initial="b782400e-3e59-412c-8f73-56cd0782301f", max_length=100)
    to_compute_transfer_destination_endpoint_id = forms.CharField(initial="d920d765-dda0-41cb-a30e-11f5a5f455a4", max_length=100)
    to_compute_transfer_source_path = forms.CharField(initial="/output/test.txt", max_length=256)
    to_compute_transfer_destination_path = forms.CharField(initial="/input/test.txt", max_length=256)
    to_compute_transfer_recursive = forms.BooleanField(initial=False, required=False)

    # Input vars for transfer 2 (ToDestination)
    from_compute_transfer_source_endpoint_id = forms.CharField(initial="d920d765-dda0-41cb-a30e-11f5a5f455a4", max_length=100)
    from_compute_transfer_destination_endpoint_id = forms.CharField(initial="b782400e-3e59-412c-8f73-56cd0782301f", max_length=100)
    from_compute_transfer_source_path = forms.CharField(initial="/output/test.txt", max_length=256)
    from_compute_transfer_destination_path = forms.CharField(initial="/input/test.txt", max_length=256)
    from_compute_transfer_recursive = forms.BooleanField(initial=False, required=False)

    # Compute Endpoint for interfacing with the compute endpoint
    compute_endpoint = forms.CharField(initial="233e6bfe-4e63-41ba-a826-40ab5a364480", disabled=True, label="Compute Node", max_length=100)

    # Load the JSON file
    
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

      # Load the JSON file
      data = []
      with open(os.path.join(settings.BASE_DIR, 'livepublication_portal', 'flows', 'flows.json'), 'r') as f:
          for line in f:
              data.append(json.loads(line))
      bee_flow_object = next(item for item in data if item["name"] == "bee-flow")
      self.compute_functions_dict = bee_flow_object["compute_functions"]
      log.debug(f"Loaded compute functions: {self.compute_functions_dict}")

      # Add fields dynamically
      for key, value in self.compute_functions_dict.items():
          self.fields[key] = forms.CharField(initial=value, disabled=True, label=key)
          log.debug(f"Added compute function {key} with value {value}")

@login_required
def bee_flow(request, uuid):
    if request.method == "POST":
        form = BeeMovieForm(request.POST)
        if form.is_valid():
            # Prepare the input data for the flow
            input_data = {
                "to_compute_transfer_source_endpoint_id": form.cleaned_data["to_compute_transfer_source_endpoint_id"],
                "to_compute_transfer_destination_endpoint_id": form.cleaned_data["to_compute_transfer_destination_endpoint_id"],
                "to_compute_transfer_source_path": form.cleaned_data["to_compute_transfer_source_path"],
                "to_compute_transfer_destination_path": form.cleaned_data["to_compute_transfer_destination_path"],
                "to_compute_transfer_recursive": form.cleaned_data["to_compute_transfer_recursive"],
                "from_compute_transfer_source_endpoint_id": form.cleaned_data["from_compute_transfer_source_endpoint_id"],
                "from_compute_transfer_destination_endpoint_id": form.cleaned_data["from_compute_transfer_destination_endpoint_id"],
                "from_compute_transfer_source_path": form.cleaned_data["from_compute_transfer_source_path"],
                "from_compute_transfer_destination_path": form.cleaned_data["from_compute_transfer_destination_path"],
                "from_compute_transfer_recursive": form.cleaned_data["from_compute_transfer_recursive"],
                "compute_endpoint": form.cleaned_data["compute_endpoint"]
            }

            # Add the dynamic fields to the input data
            for key in form.compute_functions_dict.keys():
                input_data[key] = form.cleaned_data[key]

            # Start the flow with the input data
            log.debug(f"Loading flow token for user {request.user.username}")
            token = load_globus_access_token(request.user, str(uuid))
            authorizer = globus_sdk.AccessTokenAuthorizer(token)
            sfc = globus_sdk.SpecificFlowClient(str(uuid), authorizer=authorizer)
            run = sfc.run_flow(
                body={"input":input_data},
                tags=form.cleaned_data["tags"].split(","),
                label=form.cleaned_data["label"],
            )
            log.info(
                f"Flow started with run {run.data['run_id']} for user {request.user.username}"
            )
            context = {
                'form': form,
                'run_id': run.data['run_id'],
                'flow_url': f"https://app.globus.org/runs/{run.data['run_id']}/"
            }
            return render(request, "flow-started.html", context)
        log.debug(
            f"User {request.user.username} failed to start flow due to {len(form.errors)} form errors."
        )
    else:
        log.debug(f"Loading new form for user {request.user.username}")
        form = BeeMovieForm()

    context = {'form': form}
    return render(request, "flow-init.html", context)
