import logging
import os
import globus_sdk 
import json 

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms
from globus_portal_framework.gclients import load_globus_access_token

from .flow_form import BaseFlowForm  

log = logging.getLogger(__name__)

class BeeMovieForm(BaseFlowForm):
    def __init__(self, *args, **kwargs):
        custom_fields = {
            'to_compute_transfer_source_endpoint_id': forms.CharField(
                label="Source Endpoint ID",
                initial="b782400e-3e59-412c-8f73-56cd0782301f",
                max_length=100,
                help_text="Identifier for the source Globus endpoint for initial transfer."
            ),
            'to_compute_transfer_destination_endpoint_id': forms.CharField(
                label="Destination Endpoint ID",
                initial="d920d765-dda0-41cb-a30e-11f5a5f455a4",
                max_length=100,
                help_text="Identifier for the destination Globus endpoint for initial transfer."
            ),
            'to_compute_transfer_source_path': forms.CharField(
                label="Source Path",
                initial="/output/test.txt",
                max_length=256,
                help_text="File path at the source endpoint for the initial transfer."
            ),
            'to_compute_transfer_destination_path': forms.CharField(
                label="Destination Path",
                initial="/input/test.txt",
                max_length=256,
                help_text="File path at the destination endpoint for the initial transfer."
            ),
            'to_compute_transfer_recursive': forms.BooleanField(
                label="Recursive Transfer",
                initial=False,
                required=False,
                help_text="Set to true to enable recursive transfer from the source."
            ),
            'from_compute_transfer_source_endpoint_id': forms.CharField(
                label="Source Endpoint ID (Return)",
                initial="d920d765-dda0-41cb-a30e-11f5a5f455a4",
                max_length=100,
                help_text="Identifier for the source Globus endpoint for return transfer."
            ),
            'from_compute_transfer_destination_endpoint_id': forms.CharField(
                label="Destination Endpoint ID (Return)",
                initial="b782400e-3e59-412c-8f73-56cd0782301f",
                max_length=100,
                help_text="Identifier for the destination Globus endpoint for return transfer."
            ),
            'from_compute_transfer_source_path': forms.CharField(
                label="Source Path (Return)",
                initial="/output/test.txt",
                max_length=256,
                help_text="File path at the source endpoint for the return transfer."
            ),
            'from_compute_transfer_destination_path': forms.CharField(
                label="Destination Path (Return)",
                initial="/input/test.txt",
                max_length=256,
                help_text="File path at the destination endpoint for the return transfer."
            ),
            'from_compute_transfer_recursive': forms.BooleanField(
                label="Recursive Transfer (Return)",
                initial=False,
                required=False,
                help_text="Set to true to enable recursive transfer to the destination."
            )
        }
        super().__init__(flow_name='bee-flow', extra_fields=custom_fields, *args, **kwargs)

@login_required
def bee_flow(request, uuid):
    if request.method == "POST":
        form = BeeMovieForm(request.POST)
        if form.is_valid():
            # Prepare input data from the form
            input_data = {key: form.cleaned_data[key] for key in form.fields if key in form.cleaned_data}

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
