from django.contrib import admin

# Register your models here.
from .models import DemoModel
from bgtask.client import submit


def sleep(name, timeout=3):
    import time
    print(timeout)
    time.sleep(timeout)
    print(name)
    return name


def add(modeladmin, request, queryset):
    submit(sleep, "tome", timeout=5)


@admin.register(DemoModel)
class DemoAdmin(admin.ModelAdmin):
    actions = [add]
