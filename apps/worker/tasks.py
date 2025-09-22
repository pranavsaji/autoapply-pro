from rq import Queue
from redis import Redis
from automation.form_filler import submit_application

redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
q = Queue("autoapply", connection=redis)

def enqueue_submit(job, plan):
    return q.enqueue(submit_application, job, plan, job_timeout=600)