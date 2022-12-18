import sys
import datetime
from datetime import datetime
import pandas as pd
import requests, json
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDateEdit, QLabel, QDateTimeEdit
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
        self.new_date = None
        self.flight_number = None
        self.list_of_deeds = None
        self.flights = pd.read_csv('timetables.csv')
        self.users = pd.read_csv('data_about_users.csv')
        self.possible_queries = pd.read_csv('queries.csv')
        self.todo_list = pd.read_csv('todo.csv')
        self.flag = False
        self.flag_2 = False
        self.flag_3 = False
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
        self.pushButton.show()
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
            if query_id == 2:
                if self.name in self.todo_list.values:
                    self.continueSignal.connect(self.already_list)
                    self.continueSignal.emit()
                else:
                    self.continueSignal.connect(self.new_list)
                    self.continueSignal.emit()
            if query_id == 3:
                if self.name in self.todo_list.values:
                    self.continueSignal.connect(self.show_list)
                    self.continueSignal.emit()
                else:
                    self.msg.setIcon(QMessageBox.Critical)
                    self.msg.setText("Ошибка")
                    self.msg.setInformativeText('Вашего списка дел нет в базе данных')
                    self.msg.setWindowTitle("Ошибка")
                    self.msg.exec_()
            if query_id == 4:
                self.continueSignal.connect(self.birthday)
                self.continueSignal.emit()
            if query_id == 5:
                self.textEdit.hide()
                self.pushButton.hide()
                self.label.setText('Введите дату:')
                self.label_2.setText('По завершению нажмите Enter')
                self.date_2 = QDateEdit(self)
                self.date_2.setGeometry(100, 100, 150, 40)
                self.date_2.move(50, 125)
                self.date_2.show()
                self.date_2.editingFinished.connect(self.date_method_2)
            if query_id == 6:
                self.textEdit.clear()
                self.label.setText('Введите номер рейса/поезда:')
                self.label_2.setText('Введите номер:')
                self.pushButton.clicked.disconnect()
                self.pushButton.clicked.connect(self.flight_check)


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
        self.current_date = datetime.now()
        current_date_string = self.current_date.strftime('%d/%m/%y %H:%M:%S')
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Время")
        self.msg.setInformativeText(current_date_string)
        self.msg.setWindowTitle("Время")
        self.msg.exec_()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def birthday(self):
        birth_day = self.users.loc[self.users['name'] == self.name, 'date_of_birth'].iloc[0]
        current_date = datetime.today()
        year = current_date.year
        if current_date > datetime(year,int(birth_day[3:5]),int(birth_day[0:2])):
            dt_birth = datetime((year + 1),int(birth_day[3:5]),int(birth_day[0:2]))
        else:
            dt_birth = datetime(year,int(birth_day[3:5]),int(birth_day[0:2]))
        delta = dt_birth - current_date
        delta = str(delta)
        index = delta.find(',')
        delta = delta[:index]
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Время до ДР")
        self.msg.setInformativeText(delta)
        self.msg.setWindowTitle("Время до ДР")
        self.msg.exec_()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def date_method_2(self):
        self.new_date = self.date_2.date()
        self.date_2.hide()
        self.continueSignal.connect(self.date_delta)
        self.continueSignal.emit()

    def date_delta(self):
        day = int(self.new_date.day())
        month = int(self.new_date.month())
        year = int(self.new_date.year())
        new_date = datetime(year, month, day)
        current_date = datetime.today()
        if current_date > new_date:
            delta = current_date - new_date
        else:
            delta = new_date - current_date
        delta = str(delta)
        index = delta.find(',')
        delta = delta[:index]
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Время до введённого дня")
        self.msg.setInformativeText(delta)
        self.msg.setWindowTitle("Время до введённого дня")
        self.msg.exec_()
        self.label_2.show()
        self.textEdit.show()
        self.pushButton.show()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def flight_check(self):
        self.flight_number = self.textEdit.toPlainText()
        self.textEdit.clear()
        if int(self.flight_number) in self.flights.values:
            self.flight_time = self.flights.loc[self.flights['flight_id'] ==
                                                int(self.flight_number), 'date_time'].iloc[0]
            month = self.flight_time[0:2]
            day = self.flight_time[3:5]
            year = self.flight_time[6:10]
            hours = self.flight_time[11:13]
            minutes = self.flight_time[14:]
            self.flight_time = month + '/' + day + '/' + year + ' ' + hours + ':' + minutes + ':00'
            self.flight_time = datetime.strptime(self.flight_time, '%m/%d/%Y %H:%M:%S')
            self.continueSignal.connect(self.flight_info)
            self.continueSignal.emit()
        else:
            self.continueSignal.connect(self.new_flight)
            self.continueSignal.emit()

    def new_flight(self):
        self.textEdit.hide()
        self.pushButton.hide()
        self.label.setText('Введите дату и время рейса:')
        self.label_2.setText('По завершению нажмите Enter')
        self.date_Time = QDateTimeEdit(self)
        self.date_Time.setGeometry(100, 100, 150, 40)
        self.date_Time.move(50, 125)
        self.date_Time.show()
        self.date_Time.editingFinished.connect(self.dt_method)

    def dt_method(self):
        self.flight_time = self.date_Time.dateTime().toString()
        month = self.flight_time[3:6]
        if month == 'янв':
            month = 1
            month_with_zero = '0' + str(month)
        elif month == 'фев':
            month = 2
            month_with_zero = '0' + str(month)
        elif month == 'мар':
            month = 3
            month_with_zero = '0' + str(month)
        elif month == 'апр':
            month = 4
            month_with_zero = '0' + str(month)
        elif month == 'май':
            month = 5
            month_with_zero = '0' + str(month)
        elif month == 'июн':
            month = 6
            month_with_zero = '0' + str(month)
        elif month == 'июл':
            month = 7
            month_with_zero = '0' + str(month)
        elif month == 'авг':
            month = 8
            month_with_zero = '0' + str(month)
        elif month == 'сен':
            month = 9
            month_with_zero = '0' + str(month)
        elif month == 'окт':
            month = 10
            month_with_zero = str(month)
        elif month == 'ноя':
            month = 11
            month_with_zero = str(month)
        elif month == 'дек':
            month = 12
            month_with_zero = str(month)
        day_with_zero = self.flight_time[7:9]
        hour_with_zero = self.flight_time[10:12]
        minutes_with_zero = self.flight_time[13:15]
        year = int(self.flight_time[19:])
        self.flight_time = month_with_zero + '/' + day_with_zero + '/' + str(year) + ' ' + hour_with_zero + ':' \
                           + minutes_with_zero + ':00'
        self.flight_time = datetime.strptime(self.flight_time, '%m/%d/%Y %H:%M:%S')
        flight_time_for_csv = month_with_zero + '.' + day_with_zero + '.' + str(year) + '.' + hour_with_zero + '.'\
                              + minutes_with_zero
        if self.flag_2 is False:
            new = pd.DataFrame({'flight_id': [self.flight_number], 'date_time': [flight_time_for_csv]})
            pd.concat([self.flights, new], ignore_index=True).to_csv('timetables.csv', index=False)
            self.flag_2 = True
        self.continueSignal.connect(self.flight_info)
        self.continueSignal.emit()

    def flight_info(self):
        current_time = datetime.now()
        if self.flight_time > current_time:
            delta = self.flight_time - current_time
            delta = str(delta)
            index = delta.find('.')
            delta = delta[:(index - 3)]
        else:
            delta = 'Рейс уже прошёл!'
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("О рейсе")
        self.msg.setInformativeText(delta)
        self.msg.setWindowTitle("О рейсе")
        self.msg.exec_()
        self.textEdit.show()
        self.pushButton.show()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def already_list(self):
        self.list_of_deeds = self.todo_list.loc[self.todo_list['user'] == self.name, 'to_do'].iloc[0]
        self.label.setText('Вводите каждое дело с новой строчки:')
        self.label_2.setText('По завершению нажмите "Ввод"')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.list_to_csv_old)

    def new_list(self):
        self.label.setText('Вводите каждое дело с новой строчки:')
        self.label_2.setText('По завершению нажмите "Ввод"')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.list_to_csv)

    def list_to_csv_old(self):
        self.list_new = self.textEdit.toPlainText()
        self.textEdit.clear()
        self.list_new = self.list_new.split('\n')
        for i, line in enumerate(self.list_new):
            line = line.lower()
            line = line.replace(' ', '_')
            self.list_new[i] = line
        self.list_new = '.'.join(self.list_new)
        self.list_new = self.list_of_deeds + '.' + self.list_new
        self.todo_list = self.todo_list.replace({'to_do':{self.list_of_deeds:self.list_new}})
        self.todo_list.to_csv('todo.csv', index=False)
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def list_to_csv(self):
        self.list_new = self.textEdit.toPlainText()
        self.textEdit.clear()
        self.list_new = self.list_new.split('\n')
        for i, line in enumerate(self.list_new):
            line = line.lower()
            line = line.replace(' ', '_')
            self.list_new[i] = line
        self.list_new = '.'.join(self.list_new)
        if self.flag_3 is False:
            new = pd.DataFrame({'user': [self.name], 'to_do': [self.list_new]})
            pd.concat([self.todo_list, new], ignore_index=True).to_csv('todo.csv', index=False)
            self.flag_3 = True
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)

    def show_list(self):
        self.list_of_deeds = self.todo_list.loc[self.todo_list['user'] == self.name, 'to_do'].iloc[0]
        self.list_of_deeds = self.list_of_deeds.split('.')
        output = 'Список дел:'
        for line in self.list_of_deeds:
            line = line.replace('_', ' ')
            output = output + '\n' + line
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Список дел")
        self.msg.setInformativeText(output)
        self.msg.setWindowTitle("Список дел")
        self.msg.exec_()
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.new_query)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())