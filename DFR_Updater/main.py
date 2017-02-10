import sys
from PyQt5 import QtWidgets

from UpdaterGUI import UpdaterWidget


def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = UpdaterWidget()
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
