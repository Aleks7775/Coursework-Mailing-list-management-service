from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from messagin_service.models import Mailings, Attempt, Recipient
from config.settings import EMAIL_HOST_USER

class Command(BaseCommand):
    help = 'Send newsletters to users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начало выполнения команды')
        now = timezone.now().replace(second=0, microsecond=0)
        newsletters = Mailings.objects.filter(date_first__lte=now, date_end__gte=now, status='STARTED')

        for newsletter in newsletters:
            self.stdout.write(f'Найдено рассылок: {len(newsletters)}')

            self.stdout.write(f'Начало обработки рассылки: {newsletter.id}')
            emails = newsletter.recipient.values_list('email', flat=True)

            self.stdout.write(f'Список email-адресов: {list(emails)}')
            try:
                send_mail(
                    'test message subject',
                    'test message',
                    EMAIL_HOST_USER,
                    list(emails))

                self.stdout.write(f'Письмо успешно отправлено для рассылки: {newsletter.id}')
                Attempt.objects.create(status='SUCCESS', server_response='OK', mailing=newsletter)
            except Exception as e:
                self.stdout.write(f'Ошибка при отправке: {str(e)}')
                Attempt.objects.create(status='FAILURE', server_response=str(e), mailing=newsletter)
        self.stdout.write('Выполнение команды завершено')

        total_attempts = Attempt.objects.count()
        successful_attempts = Attempt.objects.filter(status='SUCCESS').count()
        failed_attempts = Attempt.objects.filter(status='FAILURE').count()
        # print(total_attempts, successful_attempts, failed_attempts)

