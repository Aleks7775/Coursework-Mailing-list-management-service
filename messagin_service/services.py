from django.core.cache import cache

from config.settings import CACHE_ENABLE
from messagin_service.models import Recipient, Message


def get_recipient_from_cache():
    if not CACHE_ENABLE:
        return Recipient.objects.all()
    key = "client_list"
    recipient = cache.get(key)
    if recipient is not None:
        return recipient
    recipient = Recipient.objects.all()
    cache.set(key, recipient)
    return recipient


def get_message_from_cache():
    if not CACHE_ENABLE:
        return Message.objects.all()
    key = "message_list"
    message = cache.get(key)
    if message is not None:
        return message
    message = Message.objects.all()
    cache.set(key, message)
    return message
