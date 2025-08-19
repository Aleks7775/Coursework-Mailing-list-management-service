from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Создание группы Менеджеры и назначение прав"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Managers")

        permissions = [
            ("messagin_service", "mailings", "view_mailings"),
            ("messagin_service", "mailings", "disabling_mailings"),
            ("messagin_service", "recipient", "view_recipient"),
            ("users", "user", "can_block_user"),
            ("users", "user", "view_user")
        ]

        for app_label, model, codename in permissions:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission = Permission.objects.get(
                codename=codename, content_type=content_type
            )
            group.permissions.add(permission)

        group.save()
        self.stdout.write(
            self.style.SUCCESS(
                "Группа 'Managers' создана/обновлена с необходимыми правами."
            )
        )
