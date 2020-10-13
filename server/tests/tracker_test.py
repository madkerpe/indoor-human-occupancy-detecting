from help_module.csv_helper import load_csv_tracker_path
from localization.old_tracker.tracker import Tracker
from localization.localiser import Localiser

test_path = load_csv_tracker_path('../tracker_data_gen/walkaround_1.csv')

tracker = Tracker()
localiser = Localiser()

localiser.set_tracker(tracker)
tracker.add_edge((0,750,477,750))
tracker.add_edge((0,0,477,0))

localiser.update_world_co(test_path)
