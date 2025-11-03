"""数据表格模块。

提供数据表格显示和管理功能。
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class DataTableWidget(QTableWidget):
    """数据表格组件。
    
    用于显示和管理数据库记录。
    """
    
    def __init__(self, parent=None) -> None:
        """初始化数据表格。
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self._current_table_name: Optional[str] = None
        self._current_data: List[Dict[str, Any]] = []
        
        # 设置表格属性
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        
        # 设置表头
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    
    def load_data(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """加载数据到表格。
        
        Args:
            table_name: 表名
            data: 数据列表
        """
        self._current_table_name = table_name
        self._current_data = data
        
        if not data:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        
        # 获取列名
        columns = list(data[0].keys())
        
        # 设置表格大小
        self.setColumnCount(len(columns))
        self.setRowCount(len(data))
        
        # 设置表头
        self.setHorizontalHeaderLabels(columns)
        
        # 填充数据
        for row_idx, row_data in enumerate(data):
            for col_idx, column in enumerate(columns):
                value = row_data.get(column)
                
                # 处理 None 值
                if value is None:
                    display_value = ""
                elif isinstance(value, (bool, int, float)):
                    display_value = str(value)
                elif hasattr(value, 'isoformat'):  # datetime 对象
                    display_value = value.isoformat()
                else:
                    display_value = str(value)
                
                item = QTableWidgetItem(display_value)
                item.setData(Qt.ItemDataRole.UserRole, value)  # 保存原始值
                
                # 设置对齐方式
                if isinstance(value, (int, float)):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                self.setItem(row_idx, col_idx, item)
        
        # 调整列宽
        self.resizeColumnsToContents()
        
        logger.debug(f"表格数据加载完成: {table_name}，{len(data)} 条记录")
    
    def get_selected_record(self) -> Optional[Dict[str, Any]]:
        """获取选中的记录。
        
        Returns:
            选中的记录字典，如果未选中则返回 None
        """
        current_row = self.currentRow()
        if current_row < 0:
            return None
        
        # 获取列名
        columns = []
        for col in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                columns.append(header_item.text())
        
        # 构建记录字典
        record = {}
        for col, column in enumerate(columns):
            item = self.item(current_row, col)
            if item:
                record[column] = item.data(Qt.ItemDataRole.UserRole)
        
        return record
    
    def get_selected_record_id(self) -> Optional[int]:
        """获取选中记录的 ID。
        
        Returns:
            记录 ID，如果未选中则返回 None
        """
        record = self.get_selected_record()
        if record:
            return record.get('Id')
        return None
    
    def get_current_table_name(self) -> Optional[str]:
        """获取当前表格名称。
        
        Returns:
            当前表名
        """
        return self._current_table_name
    
    def refresh(self) -> None:
        """刷新表格数据。
        
        注意：此方法需要外部提供数据刷新逻辑。
        """
        pass

