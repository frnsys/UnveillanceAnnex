# Celery config.
# Broker (message queue) url.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# Result backend.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
