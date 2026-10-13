from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QScrollArea,QFrame,QMessageBox,QDialog,QFormLayout,QLineEdit,QComboBox,QDateEdit
from PyQt6.QtCore import Qt,QDate
from data import repository as repo
from psycopg2 import errors

class OrderDialog(QDialog):
    def __init__(self,parent=None,order=None):
        super().__init__(parent); self.setWindowTitle('Заказ'); self.setMinimumWidth(470); self.order=order
        form=QFormLayout(self)
        self.article=QLineEdit(order['article'] if order else '')
        self.product=self.combo('products','product_id','product_name',order['product_id'] if order else None)
        self.client=self.client_combo(order['client_id'] if order else None)
        self.status=self.combo('order_statuses','status_id','status_name',order['status_id'] if order else None)
        self.address=QLineEdit(order['pickup_address'] if order else '')
        self.order_date=QDateEdit(); self.order_date.setCalendarPopup(True); self.order_date.setDisplayFormat('dd.MM.yyyy'); self.order_date.setDate(QDate.fromString(order['order_date'].isoformat(),'yyyy-MM-dd') if order else QDate.currentDate())
        self.issued=QComboBox(); self.issued.addItem('Не выдан',False); self.issued.addItem('Выдан',True); self.issue_date=QDateEdit(); self.issue_date.setCalendarPopup(True); self.issue_date.setDisplayFormat('dd.MM.yyyy'); self.issue_date.setDate(QDate.fromString(order['issue_date'].isoformat(),'yyyy-MM-dd') if order and order['issue_date'] else QDate.currentDate()); self.issue_date.setEnabled(bool(order and order['issue_date'])); self.issued.currentIndexChanged.connect(lambda *_:self.issue_date.setEnabled(bool(self.issued.currentData())))
        if order and order['issue_date']:self.issued.setCurrentIndex(1)
        for label,w in [('Артикул заказа',self.article),('Товар',self.product),('Клиент',self.client),('Статус',self.status),('Адрес пункта выдачи',self.address),('Дата заказа',self.order_date),('Состояние выдачи',self.issued),('Дата выдачи',self.issue_date)]:form.addRow(label,w)
        buttons=QHBoxLayout(); save=QPushButton('Сохранить'); cancel=QPushButton('Отмена'); cancel.setObjectName('secondaryButton'); save.clicked.connect(self.validate); cancel.clicked.connect(self.reject); buttons.addWidget(save);buttons.addWidget(cancel);form.addRow(buttons)
    def combo(self,table,idcol,namecol,selected):
        c=QComboBox()
        for r in repo.lookup(table,idcol,namecol): c.addItem(r[namecol],r[idcol])
        if selected is not None:
            i=c.findData(selected)
            if i>=0:c.setCurrentIndex(i)
        return c
    def client_combo(self,selected):
        c=QComboBox()
        for r in repo.fetch_clients(): c.addItem(r['full_name'],r['user_id'])
        if selected is not None:
            i=c.findData(selected)
            if i>=0:c.setCurrentIndex(i)
        return c
    def validate(self):
        if not self.article.text().strip() or not self.address.text().strip():QMessageBox.warning(self,'Проверка','Заполните артикул и адрес пункта выдачи.');return
        if self.issued.currentData() and self.issue_date.date()<self.order_date.date():QMessageBox.warning(self,'Проверка','Дата выдачи не может быть раньше даты заказа.');return
        if self.product.currentData() is None or self.client.currentData() is None or self.status.currentData() is None:QMessageBox.warning(self,'Проверка','Для заказа нужны товар, клиент и статус.');return
        self.accept()
    def values(self):
        return {'article':self.article.text().strip(),'product_id':self.product.currentData(),'client_id':self.client.currentData(),'status_id':self.status.currentData(),'pickup_address':self.address.text().strip(),'order_date':self.order_date.date().toPyDate(),'issue_date':self.issue_date.date().toPyDate() if self.issued.currentData() else None}

class OrderCard(QFrame):
    def __init__(self,order,on_edit,admin):
        super().__init__(); self.setObjectName('orderCard'); row=QHBoxLayout(self); info=QVBoxLayout()
        title=QLabel(order['article']);title.setObjectName('cardTitle');info.addWidget(title)
        for txt in [f"Статус заказа: {order['status_name']}",f"Товар: {order['product_name']}",f"Клиент: {order['client_name']}",f"Адрес пункта выдачи: {order['pickup_address']}",f"Дата заказа: {order['order_date'].strftime('%d.%m.%Y')}"]:
            lab=QLabel(txt);lab.setWordWrap(True);info.addWidget(lab)
        row.addLayout(info,1); delivery=QVBoxLayout(); delivery.addWidget(QLabel('Дата доставки'))
        date=QLabel(order['issue_date'].strftime('%d.%m.%Y') if order['issue_date'] else '—');date.setObjectName('deliveryDate');delivery.addWidget(date);delivery.addStretch();row.addLayout(delivery)
        if admin:
            edit=QPushButton('Изменить');edit.clicked.connect(lambda:on_edit(order));delivery.addWidget(edit)
            delete=QPushButton('Удалить');delete.setObjectName('secondaryButton');delete.clicked.connect(lambda:on_edit(order, True));delivery.addWidget(delete)

class OrdersScreen(QWidget):
    def __init__(self,on_back):
        super().__init__();self.on_back=on_back;self.user=None;self.orders=[]
        root=QVBoxLayout(self);top=QHBoxLayout();title=QLabel('Заказы');title.setObjectName('pageTitle');top.addWidget(title);top.addStretch()
        self.add=QPushButton('Добавить заказ');self.add.clicked.connect(self.add_order);self.back=QPushButton('Назад к товарам');self.back.setObjectName('secondaryButton');self.back.clicked.connect(self.on_back);top.addWidget(self.add);top.addWidget(self.back);root.addLayout(top)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.container=QWidget();self.cards=QVBoxLayout(self.container);self.cards.setAlignment(Qt.AlignmentFlag.AlignTop);self.scroll.setWidget(self.container);root.addWidget(self.scroll)
    def set_current_user(self,user):self.user=user;self.add.setVisible(user.get('role_name')=='administrator')
    def open(self):self.reload()
    def reload(self):
        while self.cards.count():
            item=self.cards.takeAt(0);w=item.widget()
            if w:w.deleteLater()
        try:
            self.orders=repo.fetch_orders();admin=self.user and self.user.get('role_name')=='administrator'
            for o in self.orders:
                card=OrderCard(o,self.edit_order,admin);self.cards.addWidget(card)
            if not self.orders:self.cards.addWidget(QLabel('Заказов пока нет.'))
        except Exception as exc:QMessageBox.critical(self,'Ошибка загрузки заказов',str(exc))
    def add_order(self):
        if not self.user or self.user.get('role_name')!='administrator':return
        try:
            dlg=OrderDialog(self)
            if dlg.exec():repo.save_order(dlg.values());self.reload()
        except errors.UniqueViolation:QMessageBox.warning(self,'Артикул занят','Заказ с таким артикулом уже существует.')
        except Exception as exc:QMessageBox.critical(self,'Ошибка сохранения',str(exc))
    def edit_order(self,order,delete=False):
        if not self.user or self.user.get('role_name')!='administrator':return
        if delete:
            if QMessageBox.question(self,'Удаление заказа',f"Удалить заказ «{order['article']}»?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)!=QMessageBox.StandardButton.Yes:return
            try: repo.delete_order(order['order_id']); self.reload()
            except Exception as exc: QMessageBox.critical(self,'Ошибка удаления',str(exc))
            return
        try:
            dlg=OrderDialog(self,order)
            if dlg.exec():repo.save_order(dlg.values(),order['order_id']);self.reload()
        except errors.UniqueViolation:QMessageBox.warning(self,'Артикул занят','Заказ с таким артикулом уже существует.')
        except Exception as exc:QMessageBox.critical(self,'Ошибка сохранения',str(exc))
