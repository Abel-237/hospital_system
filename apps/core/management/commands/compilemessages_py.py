from django.core.management.base import BaseCommand
from django.conf import settings
from compile_translations import compile_all

class Command(BaseCommand):
    help = 'Compiles .po files to .mo files using pure-Python without requiring GNU gettext'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Compiling gettext .po catalogs to binary .mo..."))
        compile_all(settings.BASE_DIR)
        self.stdout.write(self.style.SUCCESS("All translation catalogs compiled successfully!"))
