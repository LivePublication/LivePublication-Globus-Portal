import logging
from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import login_required
from .flow_form import BaseFlowForm  
import globus_sdk
from globus_portal_framework.gclients import load_globus_access_token

log = logging.getLogger(__name__)

class HelloFlowForm(BaseFlowForm):
    def __init__(self, *args, **kwargs):
        custom_fields = {
            'echo_string': forms.CharField(
                label="Echo String",
                initial="Hello World!",
                max_length=256,
                help_text="Something to echo inside the flow",
            ),
            'sleep_time': forms.IntegerField(
                help_text="How long to pause flow execution"
            )
        }
        super().__init__(flow_name='hello-flow', extra_fields=custom_fields, *args, **kwargs)

@login_required
def hello_flow(request, uuid):
    if request.method == "POST":
        form = HelloFlowForm(request.POST)
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
                label=form.cleaned_data["label"],
                tags=form.cleaned_data["tags"].split(","),
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
        form = HelloFlowForm() 

    context = {'form': form}
    return render(request, "flow-init.html", context)
