import sys
#from googletrans import Translator
import datetime
import pandas as pd
import requests, json
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDateEdit, QLabel
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
        self.city = None
        self.users = pd.read_csv('data_about_users.csv')
        self.possible_queries = pd.read_csv('queries.csv')
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
        line = 'Здравствуйте, ' + self.name + '! Чем я могу помочь?'
        self.label.setText(line)
        self.label_2.setText('Введите свой запрос ниже:')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def user(self):
        line = 'Здравствуйте, ' + self.name + '! Чем я могу помочь?'
        self.label.setText(line)
        self.label_2.setText('Введите свой запрос ниже:')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)


    def new_query(self):
        self.label_2.setText('Введите свой запрос ниже:')
        self.query = self.textEdit.toPlainText()
        self.textEdit.clear()
        if '?' in self.query:
            self.query = self.query.replace('?', '')
        self.query = self.query.lower().replace(' ', '_')
        if self.query not in self.possible_queries.values:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("Ошибка")
            self.msg.setInformativeText('Введите запрос как указано в queries.txt')
            self.msg.setWindowTitle("Ошибка")
            self.msg.exec_()
        else:
            query_id = int(self.possible_queries.loc[self.possible_queries['query'] == self.query, 'id'].iloc[0])
            if query_id == 0:
                self.label.hide()
                self.label_2.setText('Введите название города на английском:')
                self.pushButton.clicked.disconnect()
                self.pushButton.clicked.connect(self.weather)
            if query_id == 1:
                self.continueSignal.connect(self.today)
                self.continueSignal.emit()
            #if query_id == 2:
            #here will be code
            #if query_id == 3:
            #here will be code
            if query_id == 4:
                self.continueSignal.connect(self.birthday)
                self.continueSignal.emit()


    def weather(self):
        self.city = self.textEdit.toPlainText()
        self.textEdit.clear()
        api_key = "bba742021aa5a4a7cd61a67c872edc98"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + api_key + "&q=" + self.city
        response = requests.get(complete_url)
        x = response.json()
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = 'Температура: ' + str(round(y["temp"] - 273))
            current_pressure = '\n Давление (в килопаскалях): ' + str(y["pressure"])[:-1]
            current_humidity = '\n Влажность: ' + str(y["humidity"]) + '%'
            z = x["weather"]
            #translator = Translator()
            #desc = translator.translate(str(z[0]["description"]), src='en', dest='ru')
            #weather_description = '\n '+ desc.text
            weather_description = '\n ' + str(z[0]["description"])
            weather = current_temperature + current_pressure + current_humidity + weather_description
            self.msg.setIcon(QMessageBox.Information)
            self.msg.setText("Погода")
            self.msg.setInformativeText(weather)
            self.msg.setWindowTitle("Погода")
            self.msg.exec_()
            self.label.show()
            self.pushButton.clicked.disconnect()
            self.pushButton.clicked.connect(self.new_query)
        else:
            self.label_2.setText('Город не найден')
            self.label.show()
            self.pushButton.clicked.disconnect()
            self.pushButton.clicked.connect(self.new_query)

    def today(self):
        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime('%d/%m/%y %H:%M:%S')
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Время")
        self.msg.setInformativeText(current_date_string)
        self.msg.setWindowTitle("Время")
        self.msg.exec_()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def birthday(self):
        birth_day = self.users.loc[self.users['name'] == self.name, 'date_of_birth'].iloc[1]
        dt_birth = datetime.datetime(2023,int(birth_day[3:5]),int(birth_day[0:2]))
        current_date = datetime.datetime.today()
        delta = dt_birth - current_date
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Время до ДР")
        self.msg.setInformativeText(delta)
        self.msg.setWindowTitle("Время до ДР")
        self.msg.exec_()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def date_delta(self):

        current_date = datetime.datetime.today()
        delta = dt_birth - current_date



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())