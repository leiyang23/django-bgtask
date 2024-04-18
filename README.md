## Project
 A Django background task app. 

## Usage
1. install: `pip install bgtask4django`
2. migrate: `python manage.py migrate bgtask`
3. start server: `python manage.py bgtaskserver`  

Notice: Don't forget to register the `bgtask` to the Django INSTALLED_APPS.

## How to use in django?
a demo
```python
# views.py
import time

from bgtask.client import submit


def send_email(address, title, message=None):
    # some codes...
    time.sleep(5)
    # other codes...

def register(request, *args, **kwargs):
    # some codes...
    task_id = submit(send_email, "*@*.com", "test", message="this is a test")
    if not task_id:
        print("send email fail, check log for reason")
    # other codes...
```
## Configure
Configuration should be read first from the django settings, and if not found, it should be looked up from the system environment variables.
- `BGTASK_SERVER_IP:` bgtask server listen address, default `127.0.0.1`
- `BGTASK_SERVER_PORT:` bgtask server listen port, default `23323`
- `BGTASK_WORK_THREADS:` thread number for handling task, default `10`
