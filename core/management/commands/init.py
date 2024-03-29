from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from core import models

GROUPS_PERMISSIONS = {
    settings.LOCATION_SETTERS_NAME: {
        models.QrCode: ["add", "change", "delete"],
        models.Hint: ["add", "change", "delete", "view"],
        models.LogicPuzzleHint: ["view"],
        models.Hunt: ["view"],
    },
    settings.LOGIC_PUZZLE_SETTERS_NAME: {
        models.QrCode: ["view"],
        models.Hint: ["view"],
        models.LogicPuzzleHint: ["add", "change", "delete", "view"],
        models.Hunt: ["view"],
    },
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "Create the groups necessary for the scavenger hunt and assign permissions to those groups"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:
            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:
                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(
                    GROUPS_PERMISSIONS[group_name][model_cls]
                ):
                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write(
                            "Adding " + codename + " to group " + group.__str__()
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")
