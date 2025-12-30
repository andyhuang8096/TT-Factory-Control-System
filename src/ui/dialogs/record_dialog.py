"""记录添加/编辑对话框模块。

提供通用的数据添加和编辑界面。
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QScrollArea, QWidget, QComboBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime
import logging

from src.core.database.connection import DatabaseConnection, DatabaseError

logger = logging.getLogger(__name__)


class RecordDialog(QDialog):
    """记录添加/编辑对话框类。
    
    提供通用的数据添加和编辑界面，根据表结构动态生成表单字段。
    """
    
    def __init__(self, db_connection: DatabaseConnection, table_name: str,
                 record_data: Optional[Dict[str, Any]] = None, 
                 user: Optional[str] = None,
                 parent=None) -> None:
        """初始化记录对话框。
        
        Args:
            db_connection: 数据库连接对象
            table_name: 表名
            record_data: 记录数据字典（编辑模式下提供）
            user: 当前用户名
            parent: 父窗口
        """
        super().__init__(parent)
        self.db = db_connection
        self.table_name = table_name
        self.record_data = record_data or {}
        self.user = user
        self.is_edit_mode = bool(record_data)
        
        # 存储表单字段控件
        self.field_widgets: Dict[str, QLineEdit] = {}
        
        # 设置窗口属性
        title = f"编辑记录 - {table_name}" if self.is_edit_mode else f"添加记录 - {table_name}"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # 获取表列信息
        try:
            self.columns_info = self._get_table_columns()
            self._create_ui()
        except Exception as e:
            logger.error(f"初始化记录对话框失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"初始化对话框失败: {e}")
            self.reject()
    
    def _get_table_columns(self) -> Dict[str, Dict[str, Any]]:
        """获取表的列信息。
        
        Returns:
            列信息字典，键为列名，值为列属性字典
        """
        try:
            # 查询表列信息
            query = """
                SELECT 
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.IS_NULLABLE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS c
                WHERE c.TABLE_NAME = ?
                ORDER BY c.ORDINAL_POSITION
            """
            
            results = self.db.execute_query(query, (self.table_name,))
            
            columns_info = {}
            for row in results:
                column_name = row['COLUMN_NAME']
                columns_info[column_name] = {
                    'data_type': row['DATA_TYPE'],
                    'is_nullable': row['IS_NULLABLE'] == 'YES',
                    'max_length': row['CHARACTER_MAXIMUM_LENGTH'],
                    'default': row['COLUMN_DEFAULT']
                }
            
            logger.debug(f"成功获取表 {self.table_name} 的列信息，共 {len(columns_info)} 列")
            return columns_info
        
        except Exception as e:
            logger.error(f"获取表列信息失败: {self.table_name}", exc_info=True)
            raise DatabaseError(f"获取表列信息失败: {e}") from e
    
    def _create_ui(self) -> None:
        """创建UI界面。"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        form_layout.setSpacing(10)
        
        # 排除不需要用户输入的字段
        excluded_fields = ['Id', 'CreateTime', 'UpdateTime', 'CreateUser', 'UpdateUser', 'IsDeleted']
        
        # 动态创建表单字段
        for column_name, column_info in self.columns_info.items():
            if column_name in excluded_fields:
                continue
            
            # 创建标签
            label_text = column_name
            if not column_info['is_nullable']:
                label_text += " *"  # 必填字段标记
            label = QLabel(label_text)
            
            # 根据数据类型创建不同的输入控件
            widget = self._create_field_widget(column_name, column_info)
            self.field_widgets[column_name] = widget
            
            form_layout.addRow(label, widget)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # 提示信息
        hint_label = QLabel("* 表示必填字段")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(hint_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("保存")
        save_button.setDefault(True)
        save_button.clicked.connect(self._save)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_field_widget(self, column_name: str, column_info: Dict[str, Any]) -> QLineEdit:
        """根据数据类型创建表单控件。
        
        Args:
            column_name: 列名
            column_info: 列信息
        
        Returns:
            表单控件
        """
        data_type = column_info['data_type'].lower()
        
        # 创建输入框
        widget = QLineEdit()
        
        # 设置占位符
        if column_info['is_nullable']:
            widget.setPlaceholderText(f"请输入 {column_name}（可选）")
        else:
            widget.setPlaceholderText(f"请输入 {column_name}")
        
        # 设置最大长度
        if column_info['max_length']:
            widget.setMaxLength(int(column_info['max_length']))
        
        # 如果是编辑模式，填充现有数据
        if self.is_edit_mode and column_name in self.record_data:
            value = self.record_data[column_name]
            if value is not None:
                widget.setText(str(value))
        
        return widget
    
    def _validate_data(self) -> bool:
        """验证表单数据。
        
        Returns:
            验证通过返回 True，否则返回 False
        """
        # 检查必填字段
        for column_name, column_info in self.columns_info.items():
            if column_name in ['Id', 'CreateTime', 'UpdateTime', 'CreateUser', 'UpdateUser', 'IsDeleted']:
                continue
            
            if not column_info['is_nullable']:
                widget = self.field_widgets.get(column_name)
                if widget and not widget.text().strip():
                    QMessageBox.warning(self, "验证失败", f"请填写必填字段: {column_name}")
                    widget.setFocus()
                    return False
        
        return True
    
    def _get_form_data(self) -> Dict[str, Any]:
        """获取表单数据。
        
        Returns:
            表单数据字典
        """
        data = {}
        for column_name, widget in self.field_widgets.items():
            text = widget.text().strip()
            if text:
                # 根据数据类型转换值
                column_info = self.columns_info[column_name]
                data_type = column_info['data_type'].lower()
                
                try:
                    if data_type in ['int', 'bigint', 'smallint', 'tinyint']:
                        data[column_name] = int(text)
                    elif data_type in ['decimal', 'numeric', 'float', 'real', 'money']:
                        data[column_name] = float(text)
                    elif data_type in ['bit']:
                        data[column_name] = text.lower() in ['true', '1', 'yes']
                    else:
                        data[column_name] = text
                except ValueError as e:
                    QMessageBox.warning(self, "数据格式错误", 
                                      f"字段 {column_name} 的数据格式不正确: {e}")
                    widget.setFocus()
                    return {}
        
        return data
    
    def _save(self) -> None:
        """保存记录。"""
        # 验证数据
        if not self._validate_data():
            return
        
        # 获取表单数据
        data = self._get_form_data()
        if not data:
            return
        
        try:
            from src.features.crud import CRUDOperations
            crud = CRUDOperations(self.db)
            
            if self.is_edit_mode:
                # 更新记录
                record_id = self.record_data.get('Id')
                if not record_id:
                    QMessageBox.critical(self, "错误", "无法获取记录 ID")
                    return
                
                affected_rows = crud.update.update(
                    self.table_name, 
                    record_id, 
                    data, 
                    self.user
                )
                
                if affected_rows > 0:
                    QMessageBox.information(self, "成功", "记录更新成功")
                    logger.info(f"成功更新记录: {self.table_name} ID={record_id}")
                    self.accept()
                else:
                    QMessageBox.warning(self, "警告", "未能更新记录，可能记录不存在或已被删除")
            
            else:
                # 创建记录
                record_id = crud.create.create(
                    self.table_name, 
                    data, 
                    self.user
                )
                
                if record_id:
                    QMessageBox.information(self, "成功", f"记录创建成功，ID: {record_id}")
                    logger.info(f"成功创建记录: {self.table_name} ID={record_id}")
                    self.accept()
                else:
                    QMessageBox.warning(self, "警告", "创建记录失败")
        
        except DatabaseError as e:
            QMessageBox.critical(self, "数据库错误", f"保存记录失败: {e}")
            logger.error(f"保存记录失败: {e}", exc_info=True)
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存记录失败: {e}")
            logger.error(f"保存记录失败: {e}", exc_info=True)
    
    def get_result_data(self) -> Optional[Dict[str, Any]]:
        """获取对话框结果数据。
        
        Returns:
            如果对话框被接受，返回保存的数据；否则返回 None
        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self._get_form_data()
        return None
