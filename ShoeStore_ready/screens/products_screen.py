import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QDoubleSpinBox,
    QSpinBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPixmap, QIcon

from data import repository as repo
from psycopg2 import errors


class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle('Товар')
        self.setMinimumWidth(430)
        self.product = product

        form = QFormLayout(self)

        self.name = QLineEdit(
            product['product_name'] if product else ''
        )

        self.category = self._combo(
            'categories', 'category_id', 'category_name',
            product['category_id'] if product else None
        )

        self.manufacturer = self._combo(
            'manufacturers', 'manufacturer_id', 'manufacturer_name',
            product['manufacturer_id'] if product else None
        )

        self.supplier = self._combo(
            'suppliers', 'supplier_id', 'supplier_name',
            product['supplier_id'] if product else None
        )

        self.price = QDoubleSpinBox()
        self.price.setMaximum(99999999)
        self.price.setDecimals(2)
        self.price.setValue(
            float(product['price']) if product else 0
        )

        self.stock = QSpinBox()
        self.stock.setMaximum(10000000)
        self.stock.setValue(
            int(product['quantity_in_stock']) if product else 0
        )

        self.discount = QDoubleSpinBox()
        self.discount.setMaximum(100)
        self.discount.setDecimals(2)
        self.discount.setValue(
            float(product['discount_percent']) if product else 0
        )

        self.image = QLineEdit(
            (product.get('image_path') or '') if product else ''
        )
        self.image.setPlaceholderText(
            'Например: static/images/shoes.png'
        )

        for label, widget in [
            ('Название', self.name),
            ('Категория', self.category),
            ('Производитель', self.manufacturer),
            ('Поставщик', self.supplier),
            ('Цена', self.price),
            ('Количество', self.stock),
            ('Скидка, %', self.discount),
            ('Путь к изображению', self.image)
        ]:
            form.addRow(label, widget)

        buttons = QHBoxLayout()

        save = QPushButton('Сохранить')
        cancel = QPushButton('Отмена')
        cancel.setObjectName('secondaryButton')

        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        buttons.addWidget(save)
        buttons.addWidget(cancel)
        form.addRow(buttons)

    def _combo(self, table, idcol, namecol, selected):
        combo = QComboBox()

        for row in repo.lookup(table, idcol, namecol):
            combo.addItem(row[namecol], row[idcol])

        if selected is not None:
            index = combo.findData(selected)
            if index >= 0:
                combo.setCurrentIndex(index)

        return combo

    def values(self):
        return {
            'product_name': self.name.text().strip(),
            'category_id': self.category.currentData(),
            'manufacturer_id': self.manufacturer.currentData(),
            'supplier_id': self.supplier.currentData(),
            'price': self.price.value(),
            'quantity_in_stock': self.stock.value(),
            'discount_percent': self.discount.value(),
            'image_path': self.image.text().strip() or None
        }


class ProductsScreen(QWidget):
    def __init__(self, on_open_orders, on_logout):
        super().__init__()

        self.on_open_orders = on_open_orders
        self.on_logout = on_logout
        self.user = None
        self.rows = []

        root = QVBoxLayout(self)

        top = QHBoxLayout()
        title = QLabel('Товары')
        title.setObjectName('pageTitle')
        top.addWidget(title)
        top.addStretch()

        self.orders_btn = QPushButton('Заказы')
        self.orders_btn.clicked.connect(self.on_open_orders)

        self.logout_btn = QPushButton('Выйти')
        self.logout_btn.setObjectName('secondaryButton')
        self.logout_btn.clicked.connect(self.on_logout)

        top.addWidget(self.orders_btn)
        top.addWidget(self.logout_btn)
        root.addLayout(top)

        bar = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            'Поиск по названию, категории или производителю'
        )
        self.search.textChanged.connect(self.reload)

        self.category = QComboBox()
        self.category.addItem('Все категории', None)
        self.category.currentIndexChanged.connect(self.reload)

        self.sort = QComboBox()
        self.sort.addItem('По названию', 'product_name')
        self.sort.addItem('По цене', 'price')
        self.sort.addItem('По количеству', 'quantity_in_stock')
        self.sort.addItem('По скидке', 'discount_percent')
        self.sort.currentIndexChanged.connect(self.reload)

        self.direction = QComboBox()
        self.direction.addItem('По возрастанию', 'ASC')
        self.direction.addItem('По убыванию', 'DESC')
        self.direction.currentIndexChanged.connect(self.reload)

        for widget in [
            self.search, self.category, self.sort, self.direction
        ]:
            bar.addWidget(widget)

        root.addLayout(bar)

        actions = QHBoxLayout()

        self.add_btn = QPushButton('Добавить товар')
        self.edit_btn = QPushButton('Изменить')
        self.delete_btn = QPushButton('Удалить')

        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)

        for button in [
            self.add_btn, self.edit_btn, self.delete_btn
        ]:
            actions.addWidget(button)

        actions.addStretch()
        root.addLayout(actions)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Товар', 'Категория', 'Производитель',
            'Цена', 'Скидка', 'Остаток', 'Фото'
        ])

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.doubleClicked.connect(self.edit_product)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setIconSize(QSize(80, 80))
        self.table.verticalHeader().setDefaultSectionSize(90)

        root.addWidget(self.table)

    def set_current_user(self, user):
        self.user = user

        role = user.get('role_name') if user else 'guest'
        admin = role == 'administrator'
        manager = role in ('manager', 'administrator')

        for widget in (
            self.search, self.category, self.sort, self.direction
        ):
            widget.setVisible(manager)

        self.orders_btn.setVisible(manager)

        self.add_btn.setVisible(admin)
        self.edit_btn.setVisible(admin)
        self.delete_btn.setVisible(admin)

        self.reload()

    def reload(self, *_):
        if not hasattr(self, 'table'):
            return

        try:
            categories = repo.lookup(
                'categories', 'category_id', 'category_name'
            )

            current = self.category.currentData()

            self.category.blockSignals(True)
            self.category.clear()
            self.category.addItem('Все категории', None)

            for category in categories:
                self.category.addItem(
                    category['category_name'],
                    category['category_id']
                )

            index = self.category.findData(current)
            self.category.setCurrentIndex(max(0, index))
            self.category.blockSignals(False)

            manager = (
                self.user
                and self.user.get('role_name')
                in ('manager', 'administrator')
            )

            rows = repo.fetch_products(
                self.search.text().strip() if manager else '',
                self.category.currentData() if manager else None,
                self.sort.currentData() if manager else 'product_name',
                self.direction.currentData() if manager else 'ASC'
            )

            self.rows = rows
            self.table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                values = [
                    row['product_id'],
                    row['product_name'],
                    row['category_name'],
                    row['manufacturer_name'],
                    f"{float(row['final_price']):.2f} ₽",
                    f"{float(row['discount_percent']):g}%",
                    row['quantity_in_stock']
                ]

                for j, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        row['product_id']
                    )

                    if float(row['discount_percent']) > 0:
                        item.setBackground(QColor('#FFF0EB'))

                    if int(row['quantity_in_stock']) == 0:
                        item.setForeground(QColor('#D93025'))

                    self.table.setItem(i, j, item)

                # Отображение фотографии товара
                image_path = row.get('image_path')

                if image_path:
                    path = Path(image_path)

                    if not path.is_absolute():
                        project_root = Path(__file__).resolve().parent.parent
                        path = project_root / path

                    if path.is_file():
                        pixmap = QPixmap(str(path))

                        if not pixmap.isNull():
                            pixmap = pixmap.scaled(
                                80, 80,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation
                            )

                            image_item = QTableWidgetItem()
                            image_item.setIcon(QIcon(pixmap))
                            image_item.setTextAlignment(
                                Qt.AlignmentFlag.AlignCenter
                            )
                            self.table.setItem(i, 7, image_item)

            self.table.resizeColumnsToContents()
            self.table.setColumnWidth(7, 100)

        except Exception as exc:
            self.category.blockSignals(False)
            QMessageBox.critical(
                self, 'Ошибка загрузки товаров', str(exc)
            )

    def selected(self):
        row = self.table.currentRow()

        if row < 0:
            return None

        item = self.table.item(row, 0)

        if item is None:
            return None

        product_id = item.data(Qt.ItemDataRole.UserRole)

        return next(
            (
                product for product in self.rows
                if product['product_id'] == product_id
            ),
            None
        )

    def add_product(self):
        if not self.user or self.user.get('role_name') != 'administrator':
            return

        try:
            dialog = ProductDialog(self)

            if dialog.exec():
                data = dialog.values()

                if not data['product_name']:
                    QMessageBox.warning(
                        self, 'Проверка', 'Введите название товара.'
                    )
                    return

                if (
                    data['category_id'] is None
                    or data['manufacturer_id'] is None
                    or data['supplier_id'] is None
                ):
                    QMessageBox.warning(
                        self, 'Проверка',
                        'Выберите категорию, производителя и поставщика.'
                    )
                    return

                repo.save_product(data)
                self.reload()

        except Exception as exc:
            QMessageBox.critical(
                self, 'Не удалось сохранить товар', str(exc)
            )

    def edit_product(self, *_):
        if (
            not self.user
            or self.user.get('role_name') != 'administrator'
        ):
            return

        row = self.selected()

        if not row:
            return

        try:
            dialog = ProductDialog(self, row)

            if dialog.exec():
                data = dialog.values()

                if not data['product_name']:
                    QMessageBox.warning(
                        self, 'Проверка', 'Введите название товара.'
                    )
                    return

                repo.save_product(data, row['product_id'])
                self.reload()

        except Exception as exc:
            QMessageBox.critical(
                self, 'Не удалось изменить товар', str(exc)
            )

    def delete_product(self):
        if (
            not self.user
            or self.user.get('role_name') != 'administrator'
        ):
            return

        row = self.selected()

        if not row:
            return

        answer = QMessageBox.question(
            self,
            'Удаление',
            f"Удалить товар «{row['product_name']}»?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            repo.delete_product(row['product_id'])
            self.reload()

        except errors.ForeignKeyViolation:
            QMessageBox.warning(
                self,
                'Удаление невозможно',
                'Этот товар используется в заказе. '
                'Сначала измените или удалите заказ.'
            )

        except Exception as exc:
            QMessageBox.critical(
                self, 'Ошибка удаления', str(exc)
            )
