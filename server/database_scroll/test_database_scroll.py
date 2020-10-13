from PyQt5 import QtWidgets
import sys
from ui_generated import Ui_MainWindow
from main import MyUI


start_up_with_csv = False
load_40X_sensors = True
set_time_mode = True

app = QtWidgets.QApplication(sys.argv)
MainWindow = MyUI()
ui = Ui_MainWindow()

ui.setupUi(MainWindow)
MainWindow.confirmUI(ui)

if start_up_with_csv:
    MainWindow.add_csv('csv/frame1.csv')
if load_40X_sensors:
    MainWindow.reload_db()
    for key, value in MainWindow.source_checkboxes.items():
        if 400 <= value['sensor_id'] <= 409:
            key.setChecked(True)
if set_time_mode:
    ui.timeCheckBox.setChecked(True)

MainWindow.show()
sys.exit(app.exec_())

