from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.forms import BaseInlineFormSet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .forms import *
from .utils.actions import *


class HintsInLine(admin.StackedInline):
    model = Hint
    extra = 2


class InviteInLine(admin.StackedInline):
    model = Invite
    extra = 1
    readonly_fields = ("invites",)


class TeamMemberInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    @property
    def deleted_count(self):
        # Count the number of forms marked for deletion
        return sum(1 for form in self.forms if form.cleaned_data.get("DELETE"))

    @property
    def total_count(self):
        # Count the number of forms with new items added
        return sum(
            1
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE")
        )

    def clean(self):
        super().clean()
        total_objs = self.total_count - self.deleted_count
        if total_objs > self.instance.hunt.max_team_size:
            raise ValidationError(
                f"Teams for hunt: {self.instance.hunt.name} can only have a max of {self.instance.hunt.max_team_size} members. You tried to set it to {total_objs}"
            )
        elif total_objs <= 0:
            if self.request is not None:
                messages.warning(
                    self.request,
                    f"Deleted team {self.instance.name} as there were zero members.",
                )
            self.instance.delete()


class TeamMemberInline(admin.TabularInline):
    model = Team.members.through
    formset = TeamMemberInlineFormSet


class LogicPuzzleAdmin(admin.ModelAdmin):
    list_display = ("hunt", "hint", "qr_index")
    search_fields = ("hint", "qr_index", "hunt")
    list_filter = ("hunt__name",)
    ordering = ("qr_index",)


class TeamAdmin(admin.ModelAdmin):
    readonly_fields = ("path",)
    inlines = [InviteInLine, TeamMemberInline]
    search_fields = ("name", "members__username")
    list_filter = ("hunt__name",)

    @admin.display(description="Path")
    def path(self, team):
        lines = []
        codes = QrCode.codes(team)

        for i, code in enumerate(codes):
            line = (
                f'<b style="font-size: medium;">{str(code)}</b>'
                if i >= team.current_qr_i
                else str(code)
            )
            lines.append(line)

        return mark_safe("<br>".join(lines))


class QrCodeAdmin(admin.ModelAdmin):
    fields = [
        "short",
        "location",
        "notes",
        "key",
        "image_tag",
        "image_url",
    ]
    readonly_fields = ["url", "key", "image_tag"]
    list_display = ["location", "url"]
    list_filter = (
        "hunt__name",
        (
            "hunt",
            admin.EmptyFieldListFilter,
        ),
    )
    inlines = [HintsInLine]
    form = QrCodeAdminForm

    @admin.display(description="Hint Link")
    def url(self, qr):
        if qr.id:
            return format_html(
                mark_safe('<a href="{}">{}</a>'),
                reverse("qr", kwargs=dict(key=qr.key)),
                _("Link to Hint Page"),
            )
        else:
            return ""


class HuntAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # todo: add warning if admin attempts to change path length or middle locations when hunt has started (will basically re-randomize the hunt (I THINK))

        # extras = 1 if obj.starting_location else 0
        # extras += 1 if obj.ending_location else 0
        super().save_model(request, obj, form, change)
        if obj.path_length > obj.middle_locations.count():
            messages.warning(
                request,
                "The path length is longer than the amount of locations. "
                "If you do not increase middle locations or decrease path length, "
                "the path length will be reduced to the amount of locations.",
            )
            # raise ValidationError(
            #    "The path length is longer than the amount of locations. Please increase the amount of locations or decrease the path length."
            # )


class UserAdmin(UserAdmin_):
    readonly_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    actions = [
        set_as_logic_setter,
        remove_as_logic_setter,
        set_as_location_setter,
        remove_as_location_setter,
    ]
    admin_field = list(UserAdmin_.fieldsets)
    admin_field[0][1]["fields"] = (
        "username",
    )  # Scavenger does not control or store passwords. So, we don't need this field.
    admin_field[2][1]["fields"] = tuple(
        ["send_to_admin"] + list(admin_field[2][1]["fields"])
    )

    fieldsets = tuple(
        admin_field
        + [
            (
                "Metropolis Integration (OAuth)",
                dict(fields=["metropolis_id"]),
            ),
        ]
    )


admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(QrCode, QrCodeAdmin)
admin.site.register(LogicPuzzleHint, LogicPuzzleAdmin)
admin.site.register(Hunt, HuntAdmin)
admin.site.register(Invite)
