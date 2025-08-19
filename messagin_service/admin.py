from django.contrib import admin
from messagin_service.models import Recipient, Attempt, Mailings, Message
from users.models import User


admin.site.register(Mailings)
admin.site.register(Message)


@admin.register(Recipient)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "comment")
    search_fields = ("email", "full_name")
    list_filter = ("comment",)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email")
