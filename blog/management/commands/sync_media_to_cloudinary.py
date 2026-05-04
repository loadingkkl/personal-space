import os
from pathlib import Path

import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Upload existing local media files to Cloudinary using matching public IDs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without sending files to Cloudinary.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite files that already exist in Cloudinary.',
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            raise CommandError(f'MEDIA_ROOT does not exist: {media_root}')

        files = [path for path in media_root.rglob('*') if path.is_file()]
        if not files:
            self.stdout.write(self.style.WARNING('No media files found.'))
            return

        dry_run = options['dry_run']
        if not dry_run and not os.environ.get('CLOUDINARY_URL'):
            raise CommandError('CLOUDINARY_URL is required unless --dry-run is used.')

        uploaded = 0
        for path in files:
            relative_path = path.relative_to(media_root).as_posix()
            public_id = f'media/{Path(relative_path).with_suffix("").as_posix()}'

            if dry_run:
                self.stdout.write(f'{path} -> {public_id}')
                continue

            cloudinary.uploader.upload(
                str(path),
                public_id=public_id,
                resource_type='image',
                overwrite=options['overwrite'],
            )
            uploaded += 1
            self.stdout.write(self.style.SUCCESS(f'Uploaded {relative_path}'))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'{len(files)} files ready to upload.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Uploaded {uploaded} files to Cloudinary.'))
