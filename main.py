from scheduler.scheduler import Scheduler
from manager.manager import Manager

if __name__ == '__main__':
    scheduler = Scheduler()
    manager = Manager()
    scheduler.register_task_completion_callback(manager.task_completion_callback)
    manager.register_new_task_callback(scheduler.register_new_task)
    manager.listen()
    while True:
        pass
    
