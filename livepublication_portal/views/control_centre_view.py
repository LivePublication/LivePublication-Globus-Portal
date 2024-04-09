import logging
import json
import os
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Get a logger instance
logger = logging.getLogger(__name__)

@login_required
def control_centre(request):
    flows_file_path = os.path.join(settings.BASE_DIR, 'livepublication_portal', 'flows', 'flows.json')
    flows = []

    try:
        with open(flows_file_path, 'r') as f:
            for line in f:
                flow = json.loads(line.strip())
                flows.append(flow)
        logger.info("Loaded flows from flows.json")
    except FileNotFoundError:
        logger.warning(f"File not found: {flows_file_path}")

    return render(request, 'control-centre.html', {'flows': flows})