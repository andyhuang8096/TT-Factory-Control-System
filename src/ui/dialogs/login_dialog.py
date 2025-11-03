"""登录对话框模块。

提供用户登录界面。
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import logging

from src.core.security import Authentication, AuthenticationError

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """登录对话框类。
    
    提供用户登录界面。
    """
    
    def __init__(self, auth: Authentication, parent=None) -> None:
        """初始化登录对话框。
        
        Args:
            auth: 认证对象
            parent: 父窗口
        """
        super().__init__(parent)
        self.auth = auth
        self.setWindowTitle("用户登录")
        self.setModal(True)
        self.setFixedSize(350, 180)
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """创建UI界面。"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("EasyPPID 数据库管理系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFixedWidth(80)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFixedWidth(80)
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        login_button = QPushButton("登录")
        login_button.setDefault(True)
        login_button.clicked.connect(self._login)
        button_layout.addWidget(login_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 设置焦点
        self.username_edit.setFocus()
    
    def _login(self) -> None:
        """处理登录按钮点击。"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            QMessageBox.warning(self, "警告", "请输入用户名")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            self.password_edit.setFocus()
            return
        
        try:
            if self.auth.login(username, password):
                logger.info(f"用户登录成功: {username}")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "登录失败")
        
        except AuthenticationError as e:
            QMessageBox.critical(self, "登录失败", str(e))
            self.password_edit.clear()
            self.password_edit.setFocus()
        
        except Exception as e:
            logger.error(f"登录过程出错: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"登录失败: {e}")
    
    def keyPressEvent(self, event) -> None:
        """处理按键事件。"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._login()
        else:
            super().keyPressEvent(event)

