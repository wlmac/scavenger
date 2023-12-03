import json
import os
import time

from core.models import Team
from django.core.management import BaseCommand
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        return super().default(obj)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
    
    help = "Prepares the database for the scavenger hunt. (Nukes all teams)"
    
    def handle(self, *args, **options):
        # Loop groups
        try:
            rawData = serialize("json", Team.objects.all(), cls=DjangoJSONEncoder)
            currentHunt: Team = Team.objects.first().hunt
            with open(f"{currentHunt.name}_teams.json", "w+") as f:
                json.dump(rawData, f, cls=LazyEncoder, indent=6)
            path = os.path.realpath(f.name)
            print(f"Exported data successfully to {path}")
            print(
                "You can now import this data into another database using the loaddata command."
            )
            time.sleep(2)
            print("Now nuking all teams...")
            Team.objects.all().delete()
            time.sleep(1)
            print("Nuked all teams successfully.")
        except Exception as e:
            print(e)
            print("Error exporting data, try using the dumpdata command instead.")
