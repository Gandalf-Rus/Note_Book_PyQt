import sqlite3
import sys
import easygui    # для работы с проводником
import csv
import datetime as dt

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

user_id = 0
TITLES = ['id', 'name', 'phone', 'date_of_birth']


class MyWidgetChange(QMainWindow):
    def __init__(self, parent=None):
        super(MyWidgetChange, self).__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModal)
        uic.loadUi('change_func.ui', self)  # Загружаем дизайн
        self.con = sqlite3.connect("users.db")  # подключаем базу данных
        self.setWindowTitle('Изменение записи')     # устанавливаем заголовок под разнозадачный дизайн
        self.save.setText("Сохранить изменения")       # устанавливаем имя кнопки в разнозадачном дизайне
        self.save.clicked.connect(self.change)
        global user_id
        self.user_id = user_id

        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM users WHERE id =:id", {"id": self.user_id}).fetchall()[0]
        print(result)

        self.name.setText(result[TITLES.index("name")])
        self.call_number.setText(result[TITLES.index("phone")])
        self.date.setText(result[TITLES.index("date_of_birth")])

    def change(self):
        if not self.name.text():
            self.statusBar().showMessage("Введите имя")
            return
        else:
            cur = self.con.cursor()
            que = "UPDATE users\nSET "
            que += ", ".join([f"name='{self.name.text().lower()}'",
                              f"phone='{self.call_number.text()}'",
                              f"date_of_birth='{self.date.text()}'"])
            que += "\nWHERE id =:id"
            print(que)
            cur.execute(que, {"id": self.user_id})
            self.con.commit()
            self.statusBar().showMessage("Контакт изменен")


class MyWidgetAdd(QMainWindow):
    def __init__(self, parent=None):
        super(MyWidgetAdd, self).__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModal)
        uic.loadUi('change_func.ui', self)  # Загружаем дизайн
        self.con = sqlite3.connect("users.db")  # подключаем базу данных
        self.setWindowTitle("Добавление контакта")     # устанавливаем заголовок под разнозадачный дизайн
        self.save.setText("Добавить")       # устанавливаем имя кнопки в разнозадачном дизайне
        self.save.clicked.connect(self.add_func)

    def add_func(self):
        if not self.name.text():
            self.statusBar().showMessage("Введите имя")
            return
        else:
            cur = self.con.cursor()
            que = "INSERT INTO users(name, phone, date_of_birth)"
            que += "VALUES (:name, :phone, :date)"
            print(que)
            cur.execute(que, {
                "name": self.name.text().lower(),
                "phone": self.call_number.text(),
                "date": self.date.text()
                              })
            self.con.commit()
            self.statusBar().showMessage("Контакт добавлен")


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('NOTEBOOK.ui', self)    # подключаем дизайн
        self.con = sqlite3.connect("users.db")    # подключаем базу данных
        self.setStyleSheet("#MainWindow{background-color: rgb(255, 255, 200);}")    # устанавливаем дизайн окна

        # подключаем кнопки к методам + дизайн:

        self.start_search.clicked.connect(self.search_func)     # поиск
        self.start_search.clicked.connect(self.update_table_birth_func)     # обновляем таблицу с днями рождениями
        self.start_search.setStyleSheet("background-color: rgb(255, 200, 120);")

        self.change.clicked.connect(self.change_func)     # редактирование контакта
        self.change.setStyleSheet("background-color: rgb(90, 170, 255);")

        self.add_pers.clicked.connect(self.add_func)     # добавление контакта вбазу
        self.add_pers.setStyleSheet("background-color: rgb(90, 255, 90);")

        self.delete_pers.clicked.connect(self.delete_func)     # удаление контакта из базы
        self.delete_pers.setStyleSheet("background-color: rgb(250, 110, 100);")

        self.all_contac.clicked.connect(self.all_search_func)     # поиск всех контактов
        self.all_contac.clicked.connect(self.update_table_birth_func)     # обновляем таблицу с днями рождениями
        self.all_contac.setStyleSheet("background-color: rgb(255, 200, 50);")

        self.csv.clicked.connect(self.csv_format_func)     # пкрквод в csv формат
        self.csv.setStyleSheet("background-color: rgb(170, 255, 170);")

        self.update_table_birth_func()    # Вызываем метод для заполнения таблицы с днями рождениями

    def update_table_birth_func(self):

        # запрос в БД по имени и дню рождения

        cur = self.con.cursor()
        result = cur.execute("SELECT name, date_of_birth FROM users").fetchall()

        self.label_2.setText(".".join(str(dt.date.today()).split("-")[::-1]))

        month_now, day_now = str(dt.date.today()).split("-")[1:]

        correct_person = []

        # делаем проверку и заполняем

        [correct_person.append(p) for p in result if p[1].split(".")[1] > month_now]
        [correct_person.append(p) for p in result if p[1].split(".")[1] == month_now and p[1].split(".")[0] >= day_now]

        self.birthday_at_this_mounth.setRowCount(len(correct_person))
        self.birthday_at_this_mounth.setColumnCount(2)
        self.birthday_at_this_mounth.setHorizontalHeaderLabels(["name", "date_of_birth"])

        for i, elem in enumerate(correct_person):
            for j, val in enumerate(elem):
                self.birthday_at_this_mounth.setItem(i, j, QTableWidgetItem(str(val)))

        self.birthday_at_this_mounth.setSortingEnabled(True)    # включаем сортировку

    def all_search_func(self):
        self.update_table_birth_func()
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM users").fetchall()

        # Заполнияем размеры таблицы
        self.search_result.setRowCount(len(result))
        self.search_result.setColumnCount(len(TITLES))
        self.search_result.setHorizontalHeaderLabels(TITLES)

        # Заполняем таблицу, полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.search_result.setItem(i, j, QTableWidgetItem(str(val)))

        self.statusBar().showMessage("Запрос успешно выполнен")
        self.search_result.setSortingEnabled(True)

    def search_func(self):
        self.update_table_birth_func()
        cur = self.con.cursor()

        # 1 считать текст запроса
        search_name = self.search.text().lower()
        # 2 проверяем, что оно не пустое
        if search_name == "":
            self.statusBar().showMessage("Введите запрос")
            return

        # 3 составить sql запрос
        result = cur.execute("SELECT * FROM users\n \
        WHERE (name) like :name",
                             {"name": "%" + search_name + "%"}).fetchall()

        # Заполнияем размеры таблицы
        self.search_result.setRowCount(len(result))
        self.search_result.setColumnCount(len(TITLES))
        self.search_result.setHorizontalHeaderLabels(TITLES)

        if not result:
            self.statusBar().showMessage("Данного человека нет в базе")
            return

        else:
            self.statusBar().showMessage("Запрос успешно выполнен")
            # Заполняем таблицу, полученными элементами
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.search_result.setItem(i, j, QTableWidgetItem(str(val)))

        self.search_result.setSortingEnabled(True)

    def change_func(self):
        try:
            global user_id

            user_id = self.search_result.item(
                self.search_result.currentRow(), TITLES.index("id")).text()

            ob = MyWidgetChange(self)
            ob.show()

        except AttributeError:
            self.statusBar().showMessage("Выберите контакт для редактирования")
            return

    def add_func(self):
        ob = MyWidgetAdd(self)
        ob.show()

    def delete_func(self):
        try:
            wanted_delete = self.search_result.item(
                self.search_result.currentRow(), TITLES.index("name")
            ).text()
            # Спрашиваем у пользователя подтверждение на удаление элементов
            valid = QMessageBox.question(
                self, "Удаление",
                "Вы действительно хотите удалить контакт с именем: " + wanted_delete,
                QMessageBox.Yes, QMessageBox.No)

            # Если пользователь ответил утвердительно, удаляем элементы.
            # Не забываем зафиксировать изменения
            if valid == QMessageBox.Yes:
                cur = self.con.cursor()
                cur.execute("DELETE FROM users WHERE id =:id",
                            {"id": self.search_result.item(
                                self.search_result.currentRow(), TITLES.index("id")
                            ).text()})
                self.con.commit()

                self.search_func()

        except AttributeError:
            self.statusBar().showMessage("Выберите контакт для удаления")
            return

    def csv_format_func(self):
        input_file = easygui.filesavebox()    # берем путь до места сохранения

        # устанавливаем csv формат для нужного файла

        if "." in input_file:
            input_file = input_file[:input_file.index(".")] + ".csv"
        else:
            input_file = input_file + ".csv"

        data = []

        # заполняем список словарями

        for row in range(self.search_result.rowCount()):
            row_info = {}
            for col in TITLES:
                row_info[col] = self.search_result.item(row, TITLES.index(col)).text()
            data.append(row_info)

        # открываем и записываем в файл данные из списка data

        csv_file = open(input_file, 'w')

        writer = csv.DictWriter(csv_file, fieldnames=list(data[0].keys()), delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

        csv_file.close()    # закрываем файл


# создадим функцию которая не будет "умалчивать" ошибки из PyQt

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.except_hook_ = except_hook
    sys.exit(app.exec_())
