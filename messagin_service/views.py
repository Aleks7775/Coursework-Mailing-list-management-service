from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from messagin_service.models import Recipient, Message, Mailings, Attempt
from django.urls import reverse_lazy
from messagin_service.forms import ClientForm
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect


class HomeListView(ListView):
    model = Recipient
    template_name = 'messagin_service/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailings.objects.count()
        context['active_mailings'] = Mailings.objects.filter(status='STARTED').count()
        context['unique_recipients'] = Recipient.objects.distinct().count()
        return context


class ClientListView(ListView):
    model = Recipient
    template_name = 'messagin_service/client_list.html'

    def get_queryset(self):
        user = self.request.user
        key = f"client_list{user.id}"

        """Попытка получить данные из кэша"""
        queryset = cache.get(key)
        if queryset is not None:
            return queryset

        """Логика фильтрации"""
        if user.has_perm('messagin_service.view_recipient'):
            queryset = Recipient.objects.all()
        else:
            queryset = Recipient.objects.filter(owner=self.request.user)

        # Установка данных в кэш
        cache.set(key, queryset)
        return queryset

    # def get_queryset(self):
    """Без использовании кэша"""
    #     user = self.request.user
    #     print(user.get_all_permissions())
    #     if user.has_perm('messagin_service.view_recipient'):
    #         return Recipient.objects.all()
    #     return Recipient.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = ClientForm
    template_name = 'messagin_service/client_form.html'
    success_url = reverse_lazy('messagin_service:client_list')

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        form.instance.user = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = ClientForm
    template_name = 'messagin_service/client_form.html'
    success_url = reverse_lazy('messagin_service:client_list')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "messagin_service/client_confirm_delete.html"
    success_url = reverse_lazy('messagin_service:client_list')


class MessageListView(ListView):
    model = Message
    template_name = 'messagin_service/message_list.html'

    def get_queryset(self):
        user = self.request.user
        if self.request.user.has_perm("users.can_view_all") or user.has_perm('messagin_service.can_view_message'):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messagin_service/message_form.html'
    success_url = reverse_lazy('messagin_service:message_list')

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        form.instance.user = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'messagin_service/message_form.html'
    success_url = reverse_lazy('messagin_service:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "messagin_service/message_confirm_delete.html"
    success_url = reverse_lazy('messagin_service:message_list')


class MailingsListView(ListView):
    model = Mailings
    template_name = 'messagin_service/mailings_list.html'

    def get_queryset(self):
        """Может просматривать только создатель и пользователь у которого есть права"""
        user = self.request.user
        # print(user.get_all_permissions())
        if user.has_perm('messagin_service.view_mailings'):
            return Mailings.objects.all()
        return Mailings.objects.filter(owner=self.request.user)


class MailingsCreateView(LoginRequiredMixin, CreateView):
    model = Mailings
    fields = ['date_first', 'date_end', 'status', 'message', 'recipient']
    template_name = 'messagin_service/mailings_form.html'
    success_url = reverse_lazy('messagin_service:mailings_list')

    def form_valid(self, form):
        mailings = form.save()
        user = self.request.user
        mailings.owner = user
        mailings.save()
        form.instance.user = self.request.user
        return super().form_valid(form)


class MailingsUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailings
    fields = ['date_first', 'date_end', 'status', 'message', 'recipient']
    template_name = 'messagin_service/mailings_form.html'
    success_url = reverse_lazy('messagin_service:mailings_list')


class MailingsDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailings
    template_name = "messagin_service/mailings_confirm_delete.html"
    success_url = reverse_lazy('messagin_service:mailings_list')


class AttemptListView(ListView):
    model = Attempt
    template_name = 'messagin_service/mailing_attempts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailings = Mailings.objects.filter(message__owner=self.request.user)
        attempts = Attempt.objects.filter(mailing__message__owner=self.request.user)

        context['total_mailings'] = attempts.count()
        context['successful_mailings'] = attempts.filter(status='SUCCESS').count()
        context['not_successful_mailings'] = attempts.filter(status='FAILURE').count()
        context['mailings'] = mailings
        context['attempts'] = attempts
        context['user'] = self.request.user
        return context


@permission_required('messagin_service.disabling_mailings')
def deactivate_campaign(request, mailing_id):
    mailing = get_object_or_404(Mailings, id=mailing_id)
    mailing.status = 'FINISHED'
    mailing.save()
    return redirect('messagin_service:mailings_list')


def run_custom_command(request):
    call_command('newsletter')
    return HttpResponse('Команда выполнена')
