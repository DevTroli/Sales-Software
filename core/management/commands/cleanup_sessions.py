"""
Limpa sessões expiradas do Django.

Usado no build.sh (deploy) e via cron/management command.
Sem isso, a tabela django_session cresce infinitamente em serverless
porque o cron do Django (clearsessions) nunca roda automaticamente.
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from datetime import datetime


class Command(BaseCommand):
    help = "Remove todas as sessões expiradas da tabela django_session"

    def handle(self, *args, **options):
        total_before = Session.objects.count()
        expired = Session.objects.filter(expire_date__lt=datetime.now())
        count = expired.count()
        expired.delete()
        total_after = Session.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Sessões limpas: {count} expiradas removidas "
                f"({total_before} → {total_after} restantes)"
            )
        )
