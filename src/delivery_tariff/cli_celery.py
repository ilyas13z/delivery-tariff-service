import click
from delivery_tariff.celery_app import celery_app

@click.group()
def cli():
    """CLI для запуска задач Celery вручную."""
    pass

@cli.command("run-task")
@click.argument("task_name")
def run_task(task_name):
    """Запуск задачи по имени."""
    try:
        result = celery_app.send_task(task_name)
        click.echo(f"Задача '{task_name}' запущена, id={result.id}")
    except Exception as e:
        click.echo(f"send_task failed: {e}")


if __name__ == "__main__":
    cli()
    # python cli_celery.py run-task calculate_price_delivery
