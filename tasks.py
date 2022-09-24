from workers import celery
from datetime import datetime

# to run celery
# celery -A app.celery worker -l info


@celery.task()
def just_say_hello(name):
    print("INSTIDE TASK")
    print(f"Hello {name}")
