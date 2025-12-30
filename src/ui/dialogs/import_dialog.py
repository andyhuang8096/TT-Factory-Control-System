"""数据导入对话框模块。

提供从文件导入数据的界面。
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import logging
import os

from src.core.database.connection import DatabaseConnection
from src.features.import_export.importer import DataImporter, ImportError
from src.core.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ImportThread(QThread):
    """数据导入线程。"""
    
    finished_signal = pyqtSignal(bool, str)  # 成功/失败, 消息
    
    def __init__(self, importer: DataImporter, file_path: str, 
                 table_name: str, file_type: str, user: Optional[str] = None):
        super().__init__()
        self.importer = importer
        self.file_path = file_path
        self.table_name = table_name
        self.file_type = file_type
        self.user = user
        
    def run(self):
        try:
            if self.file_type == 'csv':
                self.importer.import_csv(self.file_path, self.table_name, user=self.user)
            elif self.file_type == 'excel':
                self.importer.import_excel(self.file_path, self.table_name, user=self.user)
            elif self.file_type == 'json':
                self.importer.import_json(self.file_path, self.table_name, user=self.user)
            else:
                raise ImportError(f"不支持的文件类型: {self.file_type}")
                
            self.finished_signal.emit(True, "导入成功")
            
        except ImportError as e:
            self.finished_signal.emit(False, str(e))
        except Exception as e:
            logger.error(f"导入过程出错: {e}", exc_info=True)
            self.finished_signal.emit(False, f"未知错误: {e}")


class ImportDialog(QDialog):
    """数据导入对话框类。"""
    
    def __init__(self, db_connection: DatabaseConnection, config: ConfigManager, 
                 current_table: Optional[str] = None, user: Optional[str] = None,
                 parent=None) -> None:
        """初始化导入对话框。
        
        Args:
            db_connection: 数据库连接对象
            config: 配置管理器
            current_table: 当前选中的表名
            user: 当前用户名
            parent: 父窗口
        """
        super().__init__(parent)
        self.db = db_connection
        self.config = config
        self.user = user
        self.current_table = current_table
        
        self.importer = DataImporter(db_connection, config)
        
        self.setWindowTitle("数据导入")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self._create_ui()
        self._load_tables()
        
    def _create_ui(self) -> None:
        """创建UI界面。"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        self.file_path_label.setWordWrap(True)
        select_file_btn = QPushButton("选择文件...")
        select_file_btn.clicked.connect(self._select_file)
        file_layout.addWidget(self.file_path_label, 1)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)
        
        # 表格选择
        table_layout = QHBoxLayout()
        table_label = QLabel("目标表:")
        self.table_combo = QComboBox()
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_combo, 1)
        layout.addLayout(table_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        layout.addWidget(self.progress_bar)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_button = QPushButton("导入")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self._start_import)
        button_layout.addWidget(self.import_button)
        
        cancel_button = QPushButton("关闭")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.file_path = ""
        self.file_type = ""
        
    def _load_tables(self) -> None:
        """加载数据库表列表。"""
        try:
            # 获取所有用户表
            query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """
            results = self.db.execute_query(query)
            
            self.table_combo.clear()
            for row in results:
                name = row['TABLE_NAME']
                if name != 'sysdiagrams':  # 排除系统表
                    self.table_combo.addItem(name)
            
            # 如果有当前选中的表，默认选中它
            if self.current_table:
                index = self.table_combo.findText(self.current_table)
                if index >= 0:
                    self.table_combo.setCurrentIndex(index)
                    
        except Exception as e:
            logger.error(f"加载表列表失败: {e}", exc_info=True)
            QMessageBox.warning(self, "警告", f"加载表列表失败: {e}")
            
    def _select_file(self) -> None:
        """选择要导入的文件。"""
        file_filter = "所有支持文件 (*.csv *.xlsx *.xls *.json);;CSV 文件 (*.csv);;Excel 文件 (*.xlsx *.xls);;JSON 文件 (*.json)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "", file_filter
        )
        
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            
            # 确定文件类型
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                self.file_type = 'csv'
            elif ext in ['.xlsx', '.xls']:
                self.file_type = 'excel'
            elif ext == '.json':
                self.file_type = 'json'
            else:
                self.file_type = ''
                
            self.import_button.setEnabled(bool(self.file_type))
            
    def _start_import(self) -> None:
        """开始导入数据。"""
        table_name = self.table_combo.currentText()
        if not table_name:
            QMessageBox.warning(self, "警告", "请选择目标表")
            return
            
        if not self.file_path:
            QMessageBox.warning(self, "警告", "请选择要导入的文件")
            return
            
        # 禁用界面
        self.import_button.setEnabled(False)
        self.table_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # 启动导入线程
        self.thread = ImportThread(
            self.importer, self.file_path, table_name, self.file_type, self.user
        )
        self.thread.finished_signal.connect(self._on_import_finished)
        self.thread.start()
        
    def _on_import_finished(self, success: bool, message: str) -> None:
        """处理导入完成事件。"""
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(True)
        self.table_combo.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "导入失败", message)

