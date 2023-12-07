from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from core.models import User


@admin.action(
    permissions=["change"],
    description=_("Set selected users as a Logic Puzzle Setter"),
)
def set_as_logic_setter(modeladmin, request, queryset: QuerySet[User]):
    for user in queryset:
        user.groups.add(
            Group.objects.get_or_create(name=settings.LOGIC_PUZZLE_SETTERS_NAME)
        )


@admin.action(
    permissions=["change"],
    description=_("Remove selected users as a Logic Puzzle Setter"),
)
def remove_as_logic_setter(modeladmin, request, queryset: QuerySet[User]):
    for user in queryset:
        user.groups.remove(Group.objects.get(name=settings.LOGIC_PUZZLE_SETTERS_NAME))


@admin.action(
    permissions=["change"],
    description=_("Set selected users as a Qr Code Setter"),
)
def set_as_location_setter(modeladmin, request, queryset: QuerySet[User]):
    for user in queryset:
        user.groups.add(
            Group.objects.get_or_create(name=settings.LOCATION_SETTERS_NAME)
        )


@admin.action(
    permissions=["change"],
    description=_("Remove selected users as a Qr Code Setter"),
)
def remove_as_location_setter(modeladmin, request, queryset: QuerySet[User]):
    for user in queryset:
        user.groups.remove(Group.objects.get(name=settings.LOCATION_SETTERS_NAME))
