import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication,QMainWindow,QStackedWidget,QMessageBox
from screens.login_screen import LoginScreen
from screens.products_screen import ProductsScreen
from screens.orders_screen import OrdersScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('Магазин обуви');self.resize(1120,720);self.setMinimumSize(850,560)
        self.stack=QStackedWidget();self.setCentralWidget(self.stack)
        self.login=LoginScreen(self.on_login,self.as_guest);self.products=ProductsScreen(self.show_orders,self.logout);self.orders=OrdersScreen(self.show_products)
        for page in (self.login,self.products,self.orders):self.stack.addWidget(page)
        self.stack.setCurrentWidget(self.login)
    def on_login(self,user):
        self.products.set_current_user(user);self.orders.set_current_user(user);self.stack.setCurrentWidget(self.products)
    def as_guest(self):
        user={'user_id':None,'login':'guest','full_name':'Гость','role_name':'guest'};self.on_login(user)
    def show_orders(self):self.orders.open();self.stack.setCurrentWidget(self.orders)
    def show_products(self):self.products.reload();self.stack.setCurrentWidget(self.products)
    def logout(self):self.products.user=None;self.orders.user=None;self.login.password.clear();self.login.login.clear();self.stack.setCurrentWidget(self.login)

def main():
    app=QApplication(sys.argv)
    style=Path(__file__).resolve().parent/'styles.qss'
    if style.exists():app.setStyleSheet(style.read_text(encoding='utf-8'))
    window=MainWindow();window.show();sys.exit(app.exec())
if __name__=='__main__':main()
