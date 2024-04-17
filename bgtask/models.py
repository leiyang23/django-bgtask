from django.db.models import TextChoices

from django.db import models


class StateEnum(TextChoices):
    """
    Wait: the task has not been put into the task queue.
    Ready: task has been put into the task queue, but not executed
    Running: task is running
    Finish: task done
    """
    WAIT = "Wait"
    READY = "Ready"
    RUNNING = "Running"
    FINISH = "Finish"


class ResultEnum(TextChoices):
    SUCCESS = "Success"
    FAIL = "Fail"


# Create your models here.
class BgTask(models.Model):
    task_id = models.CharField(primary_key=True, max_length=127, verbose_name="Task ID")

    fn = models.CharField(max_length=1024, verbose_name="Function Name")
    args = models.BinaryField(max_length=1024, null=True, blank=True)
    kwargs = models.BinaryField(max_length=1024, null=True, blank=True)

    err_msg = models.CharField(max_length=1024, null=True, blank=True)

    state = models.CharField(choices=StateEnum.choices, max_length=20)
    result = models.CharField(choices=ResultEnum.choices, null=True, blank=True, max_length=20)
    return_value = models.BinaryField(max_length=1024, null=True, blank=True)

    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "django_bgtask"
