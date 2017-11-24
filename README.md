# Read messages and send a sms

Docker compose create:
 * celery-master; Celery beat to schedule ask to rapidpro for new messages and ask to modem for new messages
 * Celery worker: Celery worker process tasks
 * Flower interface:  Expose the queues and the workers
