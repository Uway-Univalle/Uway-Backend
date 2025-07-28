import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserType

class Command(BaseCommand):
    help = "Create default system admin user if none exists"

    def handle(self, *args, **options):
        User      = get_user_model()

        sys_type, _ = UserType.objects.get_or_create(
            name='SystemAdmin',
            defaults={'description': 'Administrador del sistema'}
        )

        username = os.environ.get('ADMIN_USERNAME', 'sysadmin')
        email    = os.environ.get('ADMIN_EMAIL',    'admin@example.com')
        password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')

        exists = User.objects.filter(user_type=sys_type).exists()
        if exists:
            self.stdout.write(self.style.WARNING(
                'Ya existe al menos un SystemAdmin, no se crea ninguno nuevo.'
            ))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=sys_type,
            first_name='System',
            last_name='Admin',
            is_verified=True
        )
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f'SystemAdmin creado: {username} ({email})'
        ))