import json

from django.core.management.base import BaseCommand

from blog.ops import get_deployment_health


class Command(BaseCommand):
    help = 'Check deployment health for database, storage, static assets, and environment variables.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output machine-readable JSON.',
        )

    def handle(self, *args, **options):
        health = get_deployment_health()

        if options['json']:
            self.stdout.write(json.dumps(health, ensure_ascii=False, indent=2))
            return

        self.stdout.write(f"Overall: {health['overall']}")
        self.stdout.write(f"Environment: {health['environment']}")
        self.stdout.write(f"Database: {health['database']}")
        self.stdout.write('')

        for item in health['checks']:
            self.stdout.write(
                f"[{item['status'].upper()}] {item['name']}: {item['label']} - {item['detail']}"
            )
