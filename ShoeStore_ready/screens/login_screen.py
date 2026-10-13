from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QLineEdit,QPushButton,QMessageBox,QHBoxLayout
from PyQt6.QtCore import Qt
from auth import authenticate

class LoginScreen(QWidget):
    def __init__(self,on_success,on_guest):
        super().__init__(); self.on_success=on_success; self.on_guest=on_guest
        outer=QVBoxLayout(self); outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card=QWidget(); card.setObjectName('loginCard'); card.setMaximumWidth(440)
        layout=QVBoxLayout(card); layout.setContentsMargins(32,28,32,28); layout.setSpacing(14)
        title=QLabel('Магазин обуви'); title.setObjectName('pageTitle'); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle=QLabel('Войдите в систему'); subtitle.setObjectName('muted'); subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login=QLineEdit(); self.login.setPlaceholderText('Логин')
        self.password=QLineEdit(); self.password.setPlaceholderText('Пароль'); self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self.sign_in)
        btn=QPushButton('Войти'); btn.clicked.connect(self.sign_in)
        guest=QPushButton('Продолжить как гость'); guest.setObjectName('secondaryButton'); guest.clicked.connect(self.on_guest)
        layout.addWidget(title); layout.addWidget(subtitle); layout.addSpacing(8); layout.addWidget(self.login); layout.addWidget(self.password); layout.addWidget(btn); layout.addWidget(guest)
        outer.addWidget(card)
    def sign_in(self):
        login=self.login.text().strip(); password=self.password.text()
        if not login or not password:
            QMessageBox.warning(self,'Вход','Введите логин и пароль.'); return
        try: user,error=authenticate(login,password)
        except Exception as exc:
            QMessageBox.critical(self,'Ошибка базы данных',f'Не удалось подключиться к базе данных.\n\n{exc}'); return
        if error: QMessageBox.warning(self,'Не удалось войти',error); return
        self.password.clear(); self.on_success(user)
