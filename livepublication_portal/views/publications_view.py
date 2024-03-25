import logging
from django.shortcuts import render
log = logging.getLogger(__name__)

def publications(request):
    """
    Template for the publications page
    """
    log.info(
        f"User hit publciations page. Authenticated? {request.user.is_authenticated}"
    )
    return render(request, "publications.html", {})