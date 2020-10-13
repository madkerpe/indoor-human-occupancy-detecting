from localization.localiser import Localiser

H=Localiser()
#points 5,7,8,9,10,11
H.add_calibration_point(143,74,210,304)
H.add_calibration_point(265,29,106,32)
H.add_calibration_point(264,115,287,83)
H.add_calibration_point(126,164,345,337)
H.add_calibration_point(112,31,128,342)
H.add_calibration_point(44,124,272,481)
m=H.determine_matrix()
cord=H.get_world_coords(44,124)
cord/=cord[2]
print(str(cord) +'vs' +'(272,481)')

cord = H.get_world_coords(264, 115)
cord /= cord[2]
print(str(cord) + 'vs' + '(287,83)')

cord = H.get_world_coords(265, 29)
cord /= cord[2]
print(str(cord) + 'vs' + '(106,32)')

cord = H.get_world_coords(143, 74)
cord /= cord[2]
print(str(cord) + 'vs' + '(210,304)')
cord = H.get_world_coords(126, 164)
cord /= cord[2]
print(str(cord) + 'vs' + '(345,337)')
# new points
cord = H.get_world_coords(72, 75)
cord /= cord[2]
print(str(cord) + 'vs' + '(199,415)')

