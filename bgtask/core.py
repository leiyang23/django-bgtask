# coding=utf-8
import importlib
import pickle
from datetime import datetime
from logging import getLogger
from queue import Queue, Full
from threading import Thread
from uuid import uuid4

from .models import BgTask, StateEnum, ResultEnum

log = getLogger("bgtask")


class Worker(Thread):
    def __init__(self, queue: Queue, name=None):
        super().__init__(name=name)
        self.queue = queue

    def run(self) -> None:
        while True:
            task_id = self.queue.get()
            log.debug(f"{self.name} receive task：{task_id}")

            try:
                bgtask = BgTask.objects.get(task_id=task_id)
                bgtask.state, bgtask.start_time = StateEnum.RUNNING, datetime.now()
                bgtask.save()

                # execute task
                mod_path, fn_name = bgtask.fn.split(":")
                module = importlib.import_module(mod_path)
                data = getattr(module, fn_name)(*pickle.loads(bgtask.args), **pickle.loads(bgtask.kwargs))

                bgtask.state = StateEnum.FINISH
                bgtask.result = ResultEnum.SUCCESS
                bgtask.return_value = pickle.dumps(data)
                bgtask.finish_time = datetime.now()
                bgtask.save()

                log.debug(f"{self.name} has finished task：{task_id}")
            except BgTask.DoesNotExist:
                log.warning(f"task not exist: {task_id}")

            except Exception as e:
                log.error(f"{self.name} execute task error：{e}", exc_info=True)
                bgtask.state = StateEnum.FINISH
                bgtask.result = ResultEnum.FAIL
                bgtask.finish_time = datetime.now()
                bgtask.err_msg = f"error: {e}"
                bgtask.save()

            finally:
                self.queue.task_done()


class Executor:
    def __init__(self, queue: Queue, workers=10):
        self.queue = queue
        self.workers = workers
        log.info(f"executor worker threads: {workers}, start...")
        self.ready()

    def ready(self):
        """
        1. start worker threads
        2. read task from database and put into queue
        """
        for i in range(self.workers):
            Worker(self.queue, name=f"Worker-{i}").start()

        self.reload_task_from_db()

    def daemon(self):
        """守护线程
        清理超过一定时长仍未结束的任务
        """
        pass

    def reload_task_from_db(self):
        not_finish_tasks = BgTask.objects.filter(state__in=(StateEnum.WAIT, StateEnum.READY, StateEnum.RUNNING))
        log.info(f"reload tasks what not have finished: {not_finish_tasks.count()}")
        for task in not_finish_tasks:
            self.reload_task(task)
        log.info(f"tasks reloading from database is complete")

    def submit(self, fn, *args, **kwargs) -> str:
        """put task into database and queue from client"""
        task_id = uuid4().hex
        bgtask_model = BgTask.objects.create(task_id=task_id, fn=fn, args=pickle.dumps(args),
                                             kwargs=pickle.dumps(kwargs), state=StateEnum.WAIT)
        try:
            self.queue.put(task_id, timeout=30)
            bgtask_model.state = StateEnum.READY
            log.debug(f"task has been put into queue：{task_id}")
        except Full:
            log.warning("queue is full!")
            bgtask_model.state = StateEnum.FINISH
            bgtask_model.result = ResultEnum.FAIL
            bgtask_model.start_time = datetime.now()
            bgtask_model.finish_time = datetime.now()
            bgtask_model.err_msg = "queue has full, can not add after waiting 30 seconds!"
        finally:
            bgtask_model.save()

        return task_id

    def reload_task(self, task: BgTask):
        """put task into queue from database"""
        try:
            self.queue.put(task.task_id, timeout=30)
            task.state = StateEnum.READY
            log.debug(f"task has been put into queue：{task.task_id}")
        except Full:
            log.warning("queue is full!")
            task.state = StateEnum.FINISH
            task.result = ResultEnum.FAIL
            task.start_time = datetime.now()
            task.finish_time = datetime.now()
            task.desc = "queue has full, can not add after waiting 30 seconds!"
        finally:
            task.save()
