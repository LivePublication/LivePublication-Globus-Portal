from globus_compute_sdk import Executor

from globus_compute_sdk.sdk.login_manager.whoami import print_whoami_info

print_whoami_info()

# First, define the function ...
def add_func(a, b):
    return a + b

tutorial_endpoint_id = 'dc4ed5b5-3b27-4561-9f53-d561a4993744'
# ... then create the executor, ...
with Executor(endpoint_id=tutorial_endpoint_id) as gce:
    # ... then submit for execution, ...
    future = gce.submit(add_func, 5, 10)

    # ... and finally, wait for the result
    print(future.result())