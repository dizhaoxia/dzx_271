from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.serializers import CONSENT_VERSION

User = get_user_model()


DEFAULT_ACCOUNTS = [
    {
        'phone': '13800138000',
        'password': 'admin123',
        'username': '系统管理员',
        'email': 'admin@scl90.local',
        'role': User.Role.PATIENT,
        'is_staff': True,
        'is_superuser': True,
        'title': '',
        'license_no': '',
    },
    {
        'phone': '13900139000',
        'password': 'doctor123',
        'username': '张医生',
        'email': 'doctor@scl90.local',
        'role': User.Role.DOCTOR,
        'is_staff': False,
        'is_superuser': False,
        'title': '精神科主治医师',
        'license_no': 'DOC-2024-0001',
    },
    {
        'phone': '13700137000',
        'password': 'counsel123',
        'username': '李咨询师',
        'email': 'counselor@scl90.local',
        'role': User.Role.COUNSELOR,
        'is_staff': False,
        'is_superuser': False,
        'title': '国家二级心理咨询师',
        'license_no': 'CNS-2024-0001',
    },
]


class Command(BaseCommand):
    help = '创建/更新默认账号：管理员、医生、心理咨询师各 1 位（幂等，可重复执行）'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for spec in DEFAULT_ACCOUNTS:
            password = spec.pop('password')
            is_staff = spec.pop('is_staff', False)
            is_superuser = spec.pop('is_superuser', False)

            user, created = User.objects.get_or_create(
                phone=spec['phone'],
                defaults={
                    **spec,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'consent_accepted': True,
                    'consent_accepted_at': timezone.now(),
                    'consent_version': CONSENT_VERSION,
                },
            )

            if created:
                user.set_password(password)
                user.save()
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'[新建] {spec["username"]:<10} 手机号={spec["phone"]:<15} 密码={password:<10} role={user.role}'
                ))
            else:
                changed = False
                for k, v in spec.items():
                    if getattr(user, k) != v:
                        setattr(user, k, v)
                        changed = True
                if is_staff != user.is_staff:
                    user.is_staff = is_staff
                    changed = True
                if is_superuser != user.is_superuser:
                    user.is_superuser = is_superuser
                    changed = True
                if not user.consent_accepted:
                    user.consent_accepted = True
                    user.consent_accepted_at = timezone.now()
                    user.consent_version = CONSENT_VERSION
                    changed = True
                if changed or not user.check_password(password):
                    user.set_password(password)
                    user.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'[更新] {spec["username"]:<10} 手机号={spec["phone"]:<15} 密码={password:<10} role={user.role}'
                    ))
                else:
                    self.stdout.write(self.style.MIGRATE_HEADING(
                        f'[已存在] {spec["username"]:<10} 手机号={spec["phone"]:<15} role={user.role}'
                    ))

        self.stdout.write(self.style.SQL_KEYWORD(
            f'\n完成：新建 {created_count} 个，更新 {updated_count} 个。'
        ))
