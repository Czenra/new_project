import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('C:/Users/rybka/OneDrive/Рабочий стол/QtProject/main.ui', self)
        self.pushButton.clicked.connect(self.run)

    def run(self):
        name = self.textEdit.text()
        with open("data_about_users.txt", "w") as f:
            f.write(f"{name}")
        self.label_1.setText('OK')
        self.pushButton.clicked.connect(self.test)

    def test(self):
        self.label_2.setText('OK')




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())