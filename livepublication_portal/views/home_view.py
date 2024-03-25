import logging
from django.shortcuts import render
log = logging.getLogger(__name__)

def home(request):
    """
    The simplest Django view, used to greet the user.
    """
    log.info(
        f"User hit main home page. Authenticated? {request.user.is_authenticated}"
    )
    return render(request, "home.html", {})