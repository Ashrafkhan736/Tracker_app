from workers import celery
from datetime import datetime


@celery.task()
def just_say_hello(name):
    print("INSTIDE TASK")
    print(f"Hello {name}")
