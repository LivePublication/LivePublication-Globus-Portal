import logging
import globus_sdk
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .flow_form import BaseFlowForm  
from globus_portal_framework.gclients import load_globus_access_token

log = logging.getLogger(__name__)

@login_required
def ls_flow(request, uuid):
    flow_name = 'ls-flow'  

    if request.method == "POST":
        form = BaseFlowForm(request.POST, flow_name=flow_name)
        if form.is_valid():
            log.debug(f"Loading flow token for user {request.user.username}")
            token = load_globus_access_token(request.user, str(uuid))
            authorizer = globus_sdk.AccessTokenAuthorizer(token)
            sfc = globus_sdk.SpecificFlowClient(str(uuid), authorizer=authorizer)

            # Prepare input data from the form
            input_data = {key: form.cleaned_data[key] for key in form.fields if key in form.cleaned_data}

            # Start the flow with the collected input data
            run = sfc.run_flow(
                body={"input": input_data},
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
        else:
            log.debug(
                f"User {request.user.username} failed to start flow due to {len(form.errors)} form errors."
            )
    else:
        form = BaseFlowForm(flow_name=flow_name)  # Initialize the form with the flow name

    context = {'form': form}
    return render(request, "flow-init.html", context)
