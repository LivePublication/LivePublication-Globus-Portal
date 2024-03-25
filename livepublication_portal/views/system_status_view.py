import logging
from django.shortcuts import render
log = logging.getLogger(__name__)

def system_status(request):
    """
    Template for the System Status page
    """
    log.info(
        f"User hit publciations page. Authenticated? {request.user.is_authenticated}"
    )
    return render(request, "system-status.html", {})