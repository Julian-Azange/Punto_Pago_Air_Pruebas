from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Realiza migraciones en la base de datos"

    def handle(self, *args, **options):
        self.stdout.write("Iniciando migraciones...")
        call_command("makemigrations")
        call_command("migrate")
        self.stdout.write("Migraciones completadas exitosamente.")
