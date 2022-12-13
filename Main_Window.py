import sys
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDateEdit
from PyQt5.QtCore import pyqtSignal


class MyWidget(QMainWindow):
    continueSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.msg = QMessageBox(self)
        self.value = None
        self.name = None
        self.query = None
        self.users = pd.read_csv('data_about_users.csv')
        self.flag = False
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.name = self.textEdit.toPlainText()
        self.textEdit.clear()
        if self.name == '':
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("Ошибка")
            self.msg.setInformativeText('Введите своё имя')
            self.msg.setWindowTitle("Введите имя")
            self.msg.exec_()
        else:
            if self.name in self.users.values:
                self.continueSignal.connect(self.user)
                self.continueSignal.emit()
            else:
                self.continueSignal.connect(self.date_of_birth)
                self.continueSignal.emit()

    def date_of_birth(self):
        self.label.setText('Введите свою дату рождения в формате DD/MM/YYYY:')
        self.label_2.setText('По завершению нажмите Enter')
        self.textEdit.hide()
        self.pushButton.hide()
        self.date = QDateEdit(self)
        self.date.setGeometry(100, 100, 150, 40)
        self.date.move(0, 125)
        self.date.show()
        self.date.editingFinished.connect(self.date_method)

    def date_method(self):
        self.value = self.date.date()
        self.date.hide()
        self.continueSignal.connect(self.new_user)
        self.continueSignal.emit()

    def new_user(self):
        day = str(self.value.day())
        month = str(self.value.month())
        year = str(self.value.year())
        if int(day) < 10:
            day = '0' + day
        if int(month) < 10:
            month = '0' + month
        date_of_birth = day + '.' + month + '.' + year
        if self.flag is False:
            new = pd.DataFrame({'name': [self.name], 'date_of_birth': [date_of_birth]})
            pd.concat([self.users, new], ignore_index=True).to_csv('data_about_users.csv', index=False)
            self.flag = True
        self.date.hide()
        self.textEdit.show()
        self.pushButton.show()
        line = 'Здравствуйте, ' + self.name + '! Чем я могу помочь?'
        self.label.setText(line)
        self.label_2.setText('Введите свой запрос ниже:')
        self.pushButton.clicked.connect(self.new_query)

    def user(self):
        line = 'Здравствуйте, ' + self.name + '! Чем я могу помочь?'
        self.label.setText(line)
        self.label_2.setText('Введите свой запрос ниже:')
        self.pushButton.clicked.connect(self.new_query)

    def new_query(self):
        self.query = self.textEdit.toPlainText()
        self.textEdit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())