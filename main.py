import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        self.setup_table()
        self.load_coffee_data()
        self.show()

    def setup_table(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            "ID", "Название сорта", "Степень обжарки",
            "Тип (молотый/в зернах)", "Описание вкуса",
            "Цена (руб.)", "Объем упаковки (г)"
        ])
        self.tableWidget.setColumnWidth(0, 40)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 120)
        self.tableWidget.setColumnWidth(3, 150)
        self.tableWidget.setColumnWidth(4, 250)
        self.tableWidget.setColumnWidth(5, 100)
        self.tableWidget.setColumnWidth(6, 125)

    def load_coffee_data(self):
        self.cursor.execute("SELECT id, name, roast, grind_type, flavor_description, price, volume FROM coffee")
        data = self.cursor.fetchall()
        self.tableWidget.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_idx, col_idx, item)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    sys.exit(app.exec())
