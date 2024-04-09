import logging
import os
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms

import globus_sdk
from globus_portal_framework.gclients import load_globus_access_token


log = logging.getLogger(__name__)


class lsFlowForm(forms.Form):
    """
    This is a Django form to control and validate user input fields.

    https://docs.djangoproject.com/en/4.2/topics/forms/

    Typically this would go into its own forms.py class, but it's added here for simplicity.
    """

    label = forms.CharField(
        initial="An exmaple run which lists the contents of the compute endpoint",
        max_length=256,
        help_text="A nice label to add context to this flow",
    )
    tags = forms.CharField(
        label="Tags",
        max_length=256,
        help_text="Tags help categorize many runs over time. You can use a comma separated list here.",
    )

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
      flow_object = next(item for item in data if item["name"] == "ls-flow")
      self.compute_functions_dict = flow_object["compute_functions"]
      log.debug(f"Loaded compute functions: {self.compute_functions_dict}")

      # Add fields dynamically
      for key, value in self.compute_functions_dict.items():
          self.fields[key] = forms.CharField(initial=value, disabled=True, label=key)
          log.debug(f"Added compute function {key} with value {value}")


@login_required
def ls_flow(request, uuid):
    """
    This view is the heart of this project. It behaves a few different ways.
    First, it renders the form above in normal GET requests, and allows the user to
    populate it with values.

    When a user POSTs a valid form, it loads a _user_ access token and starts the flow
    as the user with the values they provide. The JSON response is given directly to
    the template, and used to build a link to the webapp to track progress.
    """
    if request.method == "POST":
        form = lsFlowForm(request.POST)
        if form.is_valid():
            log.debug(f"Loading flow token for user {request.user.username}")
            token = load_globus_access_token(request.user, str(uuid))
            authorizer = globus_sdk.AccessTokenAuthorizer(token)
            sfc = globus_sdk.SpecificFlowClient(str(uuid), authorizer=authorizer)

            input_data = {
                "compute_endpoint": form.cleaned_data["compute_endpoint"]
            }

            # Add the dynamic fields to the input data
            for key in form.compute_functions_dict.keys():
                input_data[key] = form.cleaned_data[key]

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
        form = lsFlowForm()

    context = {'form': form}
    return render(request, "flow-init.html", context)