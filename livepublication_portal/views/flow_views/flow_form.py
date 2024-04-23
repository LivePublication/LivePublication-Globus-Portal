from django import forms
from django.conf import settings
import json
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class BaseFlowForm(forms.Form):
    # General fields for all flows
    label = forms.CharField(
        initial="Default label for a flow run",
        max_length=256,
        help_text="A nice label to add context to this flow",
    )
    tags = forms.CharField(
        initial="LivePublication, Test"
        label="Tags",
        max_length=256,
        help_text="Tags help categorize many runs over time. Use a comma-separated list.",
    )

    COMPUTE_ENDPOINT_CHOICES = (
        ('233e6bfe-4e63-41ba-a826-40ab5a364480', 'Normal'),
        ('58fb6f2d-ff78-4f39-9669-38c12d01f566', 'Experimental')
    )

    def __init__(self, *args, **kwargs):
        # Explicitly pop flow_name and extra_fields if they exist in kwargs
        flow_name = kwargs.pop('flow_name', None) 
        extra_fields = kwargs.pop('extra_fields', {})

        super().__init__(*args, **kwargs)
        self.flow_name = flow_name if flow_name else 'default-flow'
        self.extra_fields = extra_fields
        self.load_flow_config()
        self.add_extra_fields()

    def load_flow_config(self):
        # Load the JSON file containing flow configurations
        path = os.path.join(settings.BASE_DIR, 'livepublication_portal', 'flows', 'flows.json')
        with open(path, 'r') as f:
            flows_data = [json.loads(line) for line in f]
        
        flow_config = next((flow for flow in flows_data if flow['name'] == self.flow_name), None)
        if not flow_config:
            log.error(f"No configuration found for flow {self.flow_name}")
            return
        
        log.debug(f"Configuring form for {self.flow_name} with data: {flow_config}")
        
        # If the flow uses compute, configure compute-specific fields
        if flow_config.get('uses_compute'):
            self.fields['compute_endpoint'] = forms.ChoiceField(
                choices=self.COMPUTE_ENDPOINT_CHOICES,
                label="Compute Endpoint",
                help_text="Choose the compute endpoint to run the flow on",
            )

            # Dynamically add fields for compute functions
            compute_functions = flow_config.get('compute_functions', {})
            for function_key, function_id in compute_functions.items():
                self.fields[function_key] = forms.CharField(
                    initial=function_id,
                    disabled=True,
                    label=function_key,
                    help_text=f"ID for {function_key}"
                )

    def add_extra_fields(self):
        # Add any extra fields here
        for name, field in self.extra_fields.items():
            self.fields[name] = field
