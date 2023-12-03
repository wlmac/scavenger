import threading
import time


class CheckIfEmptyThread(threading.Thread):
    def __init__(self, team, **kwargs):
        self.team = team
        super(CheckIfEmptyThread, self).__init__(**kwargs)

    def run(self):
        print(
            f"Starting thread for team {self.team.name} with {self.team.members.count()}",
            flush=True,
        )
        time.sleep(3)
        print(
            f"Finished sleeping for team {self.team.name} with {self.team.members.count()}",
            flush=True,
        )
        if self.team.is_empty:
            self.team.delete()
            print(f"Deleted empty team {self.team.name}", flush=True)
