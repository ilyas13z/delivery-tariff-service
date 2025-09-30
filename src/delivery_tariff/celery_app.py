from celery import Celery
import delivery_tariff.settings as settings

settings = settings.Settings()

celery_app = Celery(
    "delivery-tariff-service",
    broker=settings.broker_celery_url,
    backend=settings.backend_celery_url,
    include=["delivery_tariff.api.tasks.parcels"],
)

celery_app.conf.timezone = settings.timezone_celery
celery_app.conf.enable_utc = True

celery_app.autodiscover_tasks(["delivery_tariff.api.tasks"])

celery_app.conf.beat_schedule = {
    "calculate-price-delivery-every-5-minutes": {
        "task": "calculate_price_delivery",
        "schedule": 300.0,
    },
}
