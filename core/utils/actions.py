from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from core.models import User


def set_group_membership(
    modeladmin, request, queryset: QuerySet[User], group_name, add=True
):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        messages.error(request, f"Group '{group_name}' does not exist.")
        return

    for user in queryset:
        if add:
            user.is_staff = True
            user.save()
            user.groups.add(group)
        else:
            user.groups.remove(group)
            if user.groups.count() == 0:
                user.is_staff = False
                user.save()


@admin.action(
    permissions=["change"],
    description=_("Set selected users as a Logic Puzzle Setter"),
)
def set_as_logic_setter(modeladmin, request, queryset: QuerySet[User]):
    set_group_membership(
        modeladmin, request, queryset, settings.LOGIC_PUZZLE_SETTERS_NAME, add=True
    )


@admin.action(
    permissions=["change"],
    description=_("Remove selected users as a Logic Puzzle Setter"),
)
def remove_as_logic_setter(modeladmin, request, queryset: QuerySet[User]):
    set_group_membership(
        modeladmin, request, queryset, settings.LOGIC_PUZZLE_SETTERS_NAME, add=False
    )


@admin.action(
    permissions=["change"],
    description=_("Set selected users as a Qr Code Setter"),
)
def set_as_location_setter(modeladmin, request, queryset: QuerySet[User]):
    set_group_membership(
        modeladmin, request, queryset, settings.LOCATION_SETTERS_NAME, add=True
    )


@admin.action(
    permissions=["change"],
    description=_("Remove selected users as a Qr Code Setter"),
)
def remove_as_location_setter(modeladmin, request, queryset: QuerySet[User]):
    set_group_membership(
        modeladmin, request, queryset, settings.LOCATION_SETTERS_NAME, add=False
    )
