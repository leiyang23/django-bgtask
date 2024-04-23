## Project

A Django background task app.  
By Bgtask, we can conveniently execute asynchronous tasks, and obtain the return data.  
The actuator runs in a separate process communicating with Django via TCP, ensuring it does not impact the main logic.

## Usage

### Install bgtask

```shell
pip install -U bgtask4django
```

### Configurations

Add `bgtask` to `INSTALLED_APPS` in settings.py.

```python
# settings.py
INSTALLED_APPS = [
    'bgtask',
    '...'
]
# Configuration should be read first from the Django settings, 
# and if not found, it should be looked up from the system environment variables.
BGTASK_SERVER_IP = "127.0.0.1"
BGTASK_SERVER_PORT = 23323
BGTASK_WORK_THREADS = 10
```

### Migrate

```shell
python manage.py migrate bgtask
```

### Run server
`bgtask` run in a separate process, which is the same runtime environment as the Django instance.
```shell
python manage.py bgtaskserver
```

## How to use in Django?

one demo

```python
# views.py
import time
import pickle

from bgtask.client import submit
from bgtask.models import BgTask, StateEnum, ResultEnum


def send_email(address, title, message=None):
    # some codes...
    time.sleep(5)
    # other codes...


def register(request, *args, **kwargs):
    # `submit` will put function's import-path into task-queue by tcp,
    # if no exception, it will return `task_id`.
    task_id = submit(send_email, "*@*.com", "test", message="this is a test")
    if not task_id:
        print("send email fail, check log for reason")
    ...

    # In other function or logic
    # if we know task_id, we can get 'Bgtask' object, and then get task state and return data
    task = BgTask.objects.get(pk=task_id)
    print(task.state)
    if task.state == StateEnum.FINISH and task.result == ResultEnum.SUCCESS:
        print(pickle.loads(task.return_value))
```
