from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _l
from django.urls import reverse
from .forms import *


class HintsInLine(admin.StackedInline):
    model = Hint
    extra = 2


class InviteInLine(admin.StackedInline):
    model = Invite
    extra = 1
    readonly_fields = ("invites",)


class LogicPuzzleAdmin(admin.ModelAdmin):
    list_display = (
        "qr_index",
        "hint",
    )
    search_fields = (
        "hint",
        "qr_index",
    )
    ordering = ("qr_index",)


@admin.action(description="Mark selected teams as inactive")
def set_inactive(modeladmin, request, queryset):
    if request.user.is_superuser:
        queryset.update(is_active=False)


@admin.action(description="Mark selected teams as active")
def set_active(
    modeladmin, request, queryset
):  # note you could probably remove this one.
    if request.user.is_superuser:
        queryset.update(is_active=True)


class TeamAdmin(admin.ModelAdmin):
    readonly_fields = ("path",)
    inlines = [
        InviteInLine,
    ]
    actions = [set_inactive, set_active]

    @admin.display(description="Path")
    def path(self, team):
        return "\n".join(
            map(lambda pk: str(QrCode.objects.get(id=pk)), QrCode.code_pks(team))
        )


class QrCodeAdmin(admin.ModelAdmin):
    fields = ["short", "location", "notes", "key"]
    readonly_fields = ["url", "key"]
    list_display = ["location", "url"]
    inlines = [HintsInLine]
    form = QrCodeAdminForm

    @admin.display(description="Hint Link")
    def url(self, qr):
        if qr.id:
            return format_html(
                mark_safe('<a href="{}">{}</a>'),
                (url := reverse("qr", kwargs=dict(key=qr.key))),
                _l("Link to Hint Page"),
            )
        else:
            return ""


class UserAdmin(UserAdmin_):
    readonly_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    admin_field = list(UserAdmin_.fieldsets)
    admin_field[0][1]["fields"] = (
        "username",
    )  # passwords are not controlled by scavenger. So we don't need this field.
    fieldsets = tuple(
        admin_field
        + [
            ("Metropolis Integration (OAuth)", dict(fields=["metropolis_id"])),
            ("Game", dict(fields=["team"])),
        ]
    )


admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(QrCode, QrCodeAdmin)
admin.site.register(LogicPuzzleHint, LogicPuzzleAdmin)
