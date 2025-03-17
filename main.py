import sys
import sqlite3
from PyQt6 import QtWidgets, uic


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.tableWidget = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.addButton = self.findChild(QtWidgets.QPushButton, "addButton")
        self.editButton = self.findChild(QtWidgets.QPushButton, "editButton")
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        self.setup_table()
        self.load_coffee_data()
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)
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
        self.tableWidget.setColumnWidth(6, 123)

    def load_coffee_data(self):
        self.cursor.execute("SELECT id, name, roast, grind_type, flavor_description, price, volume FROM coffee")
        data = self.cursor.fetchall()
        self.tableWidget.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_idx, col_idx, item)

    def add_coffee(self):
        dialog = AddEditCoffeeForm(self)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_coffee_data()

    def edit_coffee(self):
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
            return
        row = selected_rows[0].row()
        coffee_id = self.tableWidget.item(row, 0).text()
        dialog = AddEditCoffeeForm(self, coffee_id)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_coffee_data()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


class AddEditCoffeeForm(QtWidgets.QDialog):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.comboGrindType = self.findChild(QtWidgets.QComboBox, "comboGrindType")
        self.buttonSave = self.findChild(QtWidgets.QPushButton, "buttonSave")
        self.buttonCancel = self.findChild(QtWidgets.QPushButton, "buttonCancel")
        self.editName = self.findChild(QtWidgets.QLineEdit, "editName")
        self.editRoast = self.findChild(QtWidgets.QLineEdit, "editRoast")
        self.editFlavor = self.findChild(QtWidgets.QPlainTextEdit, "editFlavor")
        self.spinPrice = self.findChild(QtWidgets.QDoubleSpinBox, "spinPrice")
        self.spinVolume = self.findChild(QtWidgets.QSpinBox, "spinVolume")
        self.conn = sqlite3.connect('coffee.sqlite')
        self.cursor = self.conn.cursor()
        self.comboGrindType.addItems(["В зернах", "Молотый"])
        self.coffee_id = coffee_id

        if coffee_id:
            self.setWindowTitle("Редактировать запись о кофе")
            self.load_coffee_data(coffee_id)
        else:
            self.setWindowTitle("Добавить новый кофе")

        self.buttonSave.clicked.connect(self.save_coffee)
        self.buttonCancel.clicked.connect(self.reject)

    def load_coffee_data(self, coffee_id):
        self.cursor.execute(
            "SELECT name, roast, grind_type, flavor_description, price, volume FROM coffee WHERE id = ?",
            (coffee_id,)
        )
        data = self.cursor.fetchone()
        if data:
            self.editName.setText(data[0])
            self.editRoast.setText(data[1])
            self.comboGrindType.setCurrentText(data[2])
            self.editFlavor.setPlainText(data[3])
            self.spinPrice.setValue(float(data[4]))
            self.spinVolume.setValue(int(data[5]))

    def save_coffee(self):
        name = self.editName.text()
        roast = self.editRoast.text()
        grind_type = self.comboGrindType.currentText()
        flavor = self.editFlavor.toPlainText()
        price = self.spinPrice.value()
        volume = self.spinVolume.value()
        if not name or not roast:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
            return
        try:
            if self.coffee_id:
                self.cursor.execute(
                    """UPDATE coffee 
                    SET name=?, roast=?, grind_type=?, flavor_description=?, price=?, volume=? 
                    WHERE id=?""",
                    (name, roast, grind_type, flavor, price, volume, self.coffee_id)
                )
            else:
                self.cursor.execute(
                    """INSERT INTO coffee (name, roast, grind_type, flavor_description, price, volume)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (name, roast, grind_type, flavor, price, volume)
                )
            self.conn.commit()
            self.accept()
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка базы данных", str(e))

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    sys.exit(app.exec())
