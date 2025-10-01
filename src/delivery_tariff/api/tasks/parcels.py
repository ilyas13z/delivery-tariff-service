from delivery_tariff.db.dals import PackageDALSync
from delivery_tariff.db.session import sync_session, get_exchange_rate
from celery import shared_task


@shared_task(name="calculate_price_delivery")
def calculate_price_delivery():
    with sync_session() as session:
        session.begin()

        package_dal = PackageDALSync(session)

        package_dal.update_price_delivery(get_exchange_rate("USD"))

        session.commit()
