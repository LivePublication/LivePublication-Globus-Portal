# LivePublication o-server

This orchestration server is build on top of the Globus Portal Framework towards supporting the continual execution of LivePublication Globus-Gladier flows.

Before you start, you need app credentials to run the portal. Create your [app credentials](https://app.globus.org/settings/developers/registration/confidential_client/select-project) inside `livepublication_portal/lcoal_settings.py` with the following:

```
SOCIAL_AUTH_GLOBUS_KEY = "key"
SOCIAL_AUTH_GLOBUS_SECRET = "secret"
```

1. Install requirements -- `pip install -r requirements.txt`
2. Create your flow -- gladier flow recipies are found in the `flows/` diectory. Run each recipy to register the flows with Globus.
   1. e.g. `python livepublication_portal/flows/BeeMovie/flow.py` to regester this flow with Globus and the portal. Note that this should populate the registry of flows `livepublication_portal/flows/flows.json` which is used to populate the control center flow options. 
3. Migrate your Django auth models -- `python manage.py migrate`
4. Start your server -- `python manage.py runserver`

After that, you can navigate through `http://localhost:8000/`, and start the flow you deployed in the step
above, as a user within the Django Portal. Note that only users within the Globus Group set on the flow
may run the flow. Runnable_by may also be modified via the webapp.


## My Flows not working!

An area to start building out with common painpoints.

### Notes

Gunicorn server - run from inside LivePublication-Globus-portal `gunicorn --bind <host>:<port> wsgi:application`