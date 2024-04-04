from django.urls import include, path
from . import views

urlpatterns = [
    # Our custom views
    path("", views.home, name="home"),
    path("hello-flow/<uuid:uuid>/", views.hello_flow, name="hello-flow"),
    path("bee-flow/<uuid:uuid>/", views.bee_flow, name="bee-flow"),
    path("ls-flow/<uuid:uuid>/", views.ls_flow, name="ls-flow"),
    path("publications/", views.publications, name="publications"),
    path("system-status/", views.system_status, name="system-status"),
    path("control-centre/", views.control_centre, name="control-centre"),
    # Used for login/logout
    path("", include("globus_portal_framework.urls")),
    path("", include("social_django.urls", namespace="social")),
]

