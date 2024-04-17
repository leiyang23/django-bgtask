from django.contrib import admin

from .models import BgTask


# Register your models here.
@admin.register(BgTask)
class BgtaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "fn", "state", "result", "start_time", "finish_time"]
