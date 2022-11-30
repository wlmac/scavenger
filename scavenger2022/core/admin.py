from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class HintsInLine(admin.StackedInline):
    model = Hint
    extra = 2


class InviteInLine(admin.StackedInline):
    model = Invite
    extra = 1
    readonly_fields = ("invites",)


class TeamAdmin(admin.ModelAdmin):
    readonly_fields = ("current_qr_code",)
    inlines = [
        InviteInLine,
    ]


class QrCodeAdmin(admin.ModelAdmin):
    fields = ["location"]
    list_display = ["location", "uri"]
    inlines = [HintsInLine]


admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(QrCode, QrCodeAdmin)
