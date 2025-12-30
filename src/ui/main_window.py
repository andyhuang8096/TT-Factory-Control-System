"""主窗口模块。

提供应用程序的主窗口界面。
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMenuBar, QMenu, QToolBar, QStatusBar, QLabel,
    QMessageBox, QPushButton, QSplitter, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
import logging
from datetime import datetime

from src.core.config.config_manager import ConfigManager
from src.core.database.connection import DatabaseConnection
from src.core.database import DatabaseConnectionFactory
from src.core.security import Authentication, Permissions
from src.features.crud import CRUDOperations
from src.ui.widgets import DataTableWidget
from src.features.crud import CRUDOperations
from src.ui.widgets import DataTableWidget
from src.ui.dialogs import LoginDialog, RecordDialog, ImportDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口类。
    
    应用程序的主窗口，包含菜单栏、工具栏、数据表格等。
    """
    
    def __init__(self, config: ConfigManager) -> None:
        """初始化主窗口。
        
        Args:
            config: 配置管理器
        """
        super().__init__()
        self.config = config
        
        # 初始化组件
        self.db_connection: Optional[DatabaseConnection] = None
        self.auth: Optional[Authentication] = None
        self.permissions: Optional[Permissions] = None
        self.crud: Optional[CRUDOperations] = None
        self.current_table_name: Optional[str] = None
        
        # 设置窗口属性
        self.setWindowTitle("TT_PPID_CS 数据库管理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建布局
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 初始化UI组件
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_data_table()
        
        # 连接数据库
        if not self._connect_database():
            return
        
        # 显示登录对话框
        if not self._show_login_dialog():
            self.close()
            return
        
        # 加载初始数据
        self._load_table_list()
    
    def _create_menu_bar(self) -> None:
        """创建菜单栏。"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 导入操作
        import_action = QAction("导入数据(&I)", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_data)
        file_menu.addAction(import_action)
        
        # 导出操作
        export_action = QAction("导出数据(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 数据菜单
        data_menu = menubar.addMenu("数据(&D)")
        
        # 刷新
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_data)
        data_menu.addAction(refresh_action)
        
        # 添加记录
        add_action = QAction("添加记录(&A)", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self._add_record)
        data_menu.addAction(add_action)
        
        # 编辑记录
        edit_action = QAction("编辑记录(&E)", self)
        edit_action.setShortcut("Ctrl+U")
        edit_action.triggered.connect(self._edit_record)
        data_menu.addAction(edit_action)
        
        # 删除记录
        delete_action = QAction("删除记录(&D)", self)
        delete_action.setShortcut("Ctrl+Delete")
        delete_action.triggered.connect(self._delete_record)
        data_menu.addAction(delete_action)
        
        # 备份菜单
        backup_menu = menubar.addMenu("备份(&B)")
        
        # 备份数据库
        backup_action = QAction("备份数据库(&B)", self)
        backup_action.triggered.connect(self._backup_database)
        backup_menu.addAction(backup_action)
        
        # 恢复数据库
        restore_action = QAction("恢复数据库(&R)", self)
        restore_action.triggered.connect(self._restore_database)
        backup_menu.addAction(restore_action)
        
        # 报表菜单
        report_menu = menubar.addMenu("报表(&R)")
        
        # 查看统计
        stats_action = QAction("统计信息(&S)", self)
        stats_action.triggered.connect(self._show_statistics)
        report_menu.addAction(stats_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self) -> None:
        """创建工具栏。"""
        toolbar = QToolBar("主工具栏")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # 刷新按钮
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self._refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 添加按钮
        add_action = QAction("添加", self)
        add_action.triggered.connect(self._add_record)
        toolbar.addAction(add_action)
        
        # 编辑按钮
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self._edit_record)
        toolbar.addAction(edit_action)
        
        # 删除按钮
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self._delete_record)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # 导入按钮
        import_action = QAction("导入", self)
        import_action.triggered.connect(self._import_data)
        toolbar.addAction(import_action)
        
        # 导出按钮
        export_action = QAction("导出", self)
        export_action.triggered.connect(self._export_data)
        toolbar.addAction(export_action)
    
    def _create_status_bar(self) -> None:
        """创建状态栏。"""
        status_bar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        # 用户标签
        self.user_label = QLabel("未登录")
        status_bar.addPermanentWidget(self.user_label)
    
    def _create_data_table(self) -> None:
        """创建数据表格。"""
        # 创建表选择下拉框和搜索栏
        table_layout = QHBoxLayout()
        
        # 表选择
        table_label = QLabel("选择表:")
        self.table_combo = QComboBox()
        self.table_combo.setMinimumWidth(150)
        self.table_combo.currentTextChanged.connect(self._on_table_changed)
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_combo)
        
        table_layout.addStretch()
        
        # 搜索栏
        search_label = QLabel("搜索:")
        self.search_field_combo = QComboBox()
        self.search_field_combo.setPlaceholderText("选择字段")
        self.search_field_combo.setMinimumWidth(120)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词...")
        self.search_input.setFixedWidth(200)
        self.search_input.returnPressed.connect(self._search_data)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self._search_data)
        
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._refresh_data)
        
        table_layout.addWidget(search_label)
        table_layout.addWidget(self.search_field_combo)
        table_layout.addWidget(self.search_input)
        table_layout.addWidget(search_btn)
        table_layout.addWidget(reset_btn)
        
        self.main_layout.addLayout(table_layout)
        
        # 创建数据表格
        self.table = DataTableWidget()
        self.main_layout.addWidget(self.table)
    
    def _connect_database(self) -> bool:
        """连接数据库。
        
        Returns:
            连接成功返回 True，失败返回 False
        """
        try:
            self.db_connection = DatabaseConnectionFactory.create_from_config(self.config)
            
            if not self.db_connection.connect():
                QMessageBox.critical(self, "错误", "无法连接到数据库")
                return False
            
            # 测试连接
            if not self.db_connection.test_connection():
                QMessageBox.critical(self, "错误", "数据库连接测试失败")
                return False
            
            # 初始化 CRUD 操作
            self.crud = CRUDOperations(self.db_connection)
            
            # 初始化认证和权限
            self.auth = Authentication(self.db_connection)
            self.permissions = Permissions(self.auth)
            
            self.status_label.setText("数据库已连接")
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库连接失败: {e}")
            logger.error(f"数据库连接失败: {e}", exc_info=True)
            return False
    
    def _show_login_dialog(self) -> bool:
        """显示登录对话框。
        
        Returns:
            登录成功返回 True，取消或失败返回 False
        """
        if not self.auth:
            return False
        
        dialog = LoginDialog(self.auth, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            user = self.auth.get_current_user()
            if user:
                username = user.get('UserName', 'Unknown')
                role = user.get('Role', 'Unknown')
                self.user_label.setText(f"用户: {username} ({role})")
                self.status_label.setText("登录成功")
                logger.info(f"用户登录成功: {username}")
                return True
        
        return False
    
    def _load_table_list(self) -> None:
        """加载表列表。"""
        tables = [
            ('PPIDRecord', 'PPID 记录'),
            ('UserTable', '用户表'),
            ('ImportLog', '导入日志'),
            ('BackupLog', '备份日志'),
            ('AuditLog', '审计日志')
        ]
        
        self.table_combo.clear()
        for table_name, display_name in tables:
            self.table_combo.addItem(display_name, table_name)
        
        # 默认选择第一个表
        if tables:
            self.table_combo.setCurrentIndex(0)
    
    def _on_table_changed(self) -> None:
        """表选择改变时的处理。"""
        table_name = self.table_combo.currentData()
        if table_name:
            self.current_table_name = table_name
            self._load_table_data(table_name)
    
    def _load_table_data(self, table_name: str) -> None:
        """加载表数据。
        
        Args:
            table_name: 表名
        """
        if not self.crud:
            return
        
        try:
            # 检查权限
            if self.permissions:
                self.permissions.check_table_permission(table_name, 'read')
            
            # 加载数据
            data = self.crud.read.get_all(table_name, order_by='Id DESC', limit=1000)
            
            # 显示数据
            self.table.load_data(table_name, data)
            
            self.status_label.setText(f"已加载 {len(data)} 条记录")
            
            # 更新搜索字段列表
            self.search_field_combo.clear()
            if data and len(data) > 0:
                columns = list(data[0].keys())
                self.search_field_combo.addItems(columns)
                # 默认选择第一个看起来像名称的字段，或者 Id
                for col in ['Name', 'UserName', 'Title', 'Id']:
                    index = self.search_field_combo.findText(col)
                    if index >= 0:
                        self.search_field_combo.setCurrentIndex(index)
                        break
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败: {e}")
            logger.error(f"加载数据失败: {table_name}", exc_info=True)
            self.status_label.setText("加载数据失败")

    def _search_data(self) -> None:
        """搜索数据。"""
        if not self.crud:
            return
            
        table_name = self.current_table_name
        if not table_name:
            return
            
        search_field = self.search_field_combo.currentText()
        search_value = self.search_input.text().strip()
        
        if not search_field:
            return
            
        if not search_value:
            self._refresh_data()
            return
            
        try:
            results = self.crud.read.search(table_name, search_field, search_value)
            self.table.load_data(table_name, results)
            self.status_label.setText(f"搜索结果: {len(results)} 条记录")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"搜索失败: {e}")
            logger.error(f"搜索失败: {e}", exc_info=True)
    
    def _refresh_data(self) -> None:
        """刷新数据表格。"""
        if not self.crud:
            QMessageBox.warning(self, "警告", "数据库未连接")
            return
        
        if not self.current_table_name:
            QMessageBox.warning(self, "警告", "请先选择要查看的表")
            return
        
        try:
            self._load_table_data(self.current_table_name)
            self.search_input.clear()  # 清空搜索框
            self.status_label.setText("数据已刷新")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败: {e}")
            logger.error(f"刷新数据失败: {e}", exc_info=True)
    
    def _add_record(self) -> None:
        """添加记录。"""
        if not self.table_widget.current_table:
            QMessageBox.warning(self, "警告", "请先选择一个数据表")
            return
        
        table_name = self.table_widget.current_table
        
        dialog = RecordDialog(
            db_connection=self.config.db_connection,
            table_name=table_name,
            user=self.auth.current_user,
            parent=self
        )
        
        if dialog.exec():
            # 刷新数据
            self._refresh_data()
    
    def _edit_record(self) -> None:
        """编辑记录。"""
        if not self.table_widget.current_table:
            QMessageBox.warning(self, "警告", "请先选择一个数据表")
            return
        
        # 获取选中的记录
        selected_row = self.table_widget.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的记录")
            return
            
        # 获取记录ID（假设第一列是Id）
        try:
            record_id_item = self.table_widget.item(selected_row, 0)
            if not record_id_item:
                return
            record_id = int(record_id_item.text())
        except (ValueError, TypeError):
            QMessageBox.warning(self, "错误", "无法获取记录ID")
            return
            
        table_name = self.table_widget.current_table
        
        # 获取完整记录数据
        try:
            crud = CRUDOperations(self.config.db_connection)
            record_data = crud.read.get_by_id(table_name, record_id)
            
            if not record_data:
                QMessageBox.warning(self, "错误", "记录不存在或已被删除")
                self._refresh_data()
                return
                
            dialog = RecordDialog(
                db_connection=self.config.db_connection,
                table_name=table_name,
                record_data=record_data,
                user=self.auth.current_user,
                parent=self
            )
            
            if dialog.exec():
                # 刷新数据
                self._refresh_data()
                
        except Exception as e:
            logger.error(f"准备编辑记录失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"操作失败: {e}")
    
    def _delete_record(self) -> None:
        """删除记录。"""
        if not self.crud:
            QMessageBox.warning(self, "警告", "数据库未连接")
            return
        
        if not self.current_table_name:
            QMessageBox.warning(self, "警告", "请先选择要操作的表")
            return
        
        # 获取选中的记录
        record_id = self.table.get_selected_record_id()
        if not record_id:
            QMessageBox.warning(self, "警告", "请先选择要删除的记录")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条记录吗？\n（此操作将执行软删除）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 检查权限
                if self.permissions:
                    self.permissions.check_table_permission(self.current_table_name, 'delete')
                
                user = self.auth.get_current_user() if self.auth else None
                username = user.get('UserName') if user else None
                
                # 执行删除
                self.crud.delete.delete(self.current_table_name, record_id, username)
                
                QMessageBox.information(self, "成功", "记录已删除")
                self._refresh_data()
            
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除记录失败: {e}")
                logger.error(f"删除记录失败: {e}", exc_info=True)
    
    def _import_data(self) -> None:
        """导入数据。"""
        dialog = ImportDialog(
            db_connection=self.config.db_connection,
            config=self.config,
            current_table=self.table_widget.current_table,
            user=self.auth.current_user,
            parent=self
        )
        
        if dialog.exec():
            # 刷新显示
            self._refresh_data()
    
    def _export_data(self) -> None:
        """导出数据。"""
        if not self.current_table_name:
            QMessageBox.warning(self, "警告", "请先选择要导出的表")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        # 选择文件路径
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            f"{self.current_table_name}.csv",
            "CSV 文件 (*.csv);;Excel 文件 (*.xlsx);;JSON 文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            from src.features.import_export.exporter import DataExporter
            
            exporter = DataExporter(self.db_connection)
            
            # 根据文件扩展名选择导出格式
            if file_path.endswith('.csv'):
                success = exporter.export_csv(self.current_table_name, file_path)
            elif file_path.endswith('.xlsx'):
                success = exporter.export_excel(self.current_table_name, file_path)
            elif file_path.endswith('.json'):
                success = exporter.export_json(self.current_table_name, file_path)
            else:
                QMessageBox.warning(self, "警告", "不支持的文件格式")
                return
            
            if success:
                QMessageBox.information(self, "成功", f"数据已导出到: {file_path}")
                self.status_label.setText(f"数据已导出: {file_path}")
            else:
                QMessageBox.warning(self, "警告", "导出失败")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出数据失败: {e}")
            logger.error(f"导出数据失败: {e}", exc_info=True)
    
    def _backup_database(self) -> None:
        """备份数据库。"""
        try:
            from src.features.backup import DatabaseBackup
            from PyQt6.QtWidgets import QFileDialog
            
            # 选择保存路径
            default_name = f"{self.config.db_database}_{datetime.now():%Y%m%d_%H%M%S}.bak"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "备份数据库",
                default_name,
                "SQL Server 备份文件 (*.bak)"
            )
            
            if not file_path:
                return
            
            backup = DatabaseBackup(self.db_connection)
            
            # 使用 wait cursor
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            try:
                result = backup.backup(backup_path=file_path, user=self.auth.current_user)
                
                QMessageBox.information(
                    self, 
                    "成功", 
                    f"数据库备份成功！\n文件大小: {result['file_size'] / 1024 / 1024:.2f} MB"
                )
            finally:
                QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"备份失败: {e}")
            logger.error(f"备份失败: {e}", exc_info=True)
    
    def _restore_database(self) -> None:
        """恢复数据库。"""
        # 警告用户
        reply = QMessageBox.warning(
            self,
            "危险操作",
            "恢复数据库将覆盖当前所有数据且无法撤销！\n确定要继续吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        try:
            from src.features.backup import DatabaseRestore
            from PyQt6.QtWidgets import QFileDialog
            
            # 选择备份文件
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择备份文件",
                "",
                "SQL Server 备份文件 (*.bak)"
            )
            
            if not file_path:
                return
            
            restore = DatabaseRestore(self.db_connection)
            
            # 使用 wait cursor
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QApplication
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            try:
                success = restore.restore(backup_path=file_path, replace=True)
                
                if success:
                    QMessageBox.information(self, "成功", "数据库恢复成功！\n系统将自动退出，请重启应用程序。")
                    self.close()
            finally:
                QApplication.restoreOverrideCursor()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"恢复失败: {e}")
            logger.error(f"恢复失败: {e}", exc_info=True)
    
    def _show_statistics(self) -> None:
        """显示统计信息。"""
        if not self.crud:
            QMessageBox.warning(self, "警告", "数据库未连接")
            return
        
        try:
            from src.features.analytics import Analytics
            
            analytics = Analytics(self.db_connection)
            
            # 获取综合报表
            report = analytics.generate_summary_report()
            
            # 显示报表（简化版）
            report_text = f"""
综合报表
生成时间: {report.get('generated_at', 'N/A')}

数据库统计:
"""
            for table_name, stats in report.get('database_statistics', {}).items():
                report_text += f"  {table_name}: {stats.get('total_count', 0)} 条记录\n"
            
            report_text += f"\nPPID 统计:\n"
            ppid_stats = report.get('ppid_statistics', {})
            report_text += f"  总记录数: {ppid_stats.get('total_count', 0)}\n"
            report_text += f"  状态分布: {ppid_stats.get('status_distribution', {})}\n"
            
            QMessageBox.information(self, "统计信息", report_text)
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取统计信息失败: {e}")
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
    
    def _show_about(self) -> None:
        """显示关于对话框。"""
        QMessageBox.about(
            self,
            "关于",
            "TT_PPID_CS 数据库管理系统\n\n"
            "版本: 1.0.0\n"
            "基于 Python 和 PyQt6 开发"
        )
    
    def closeEvent(self, event) -> None:
        """窗口关闭事件。"""
        if self.db_connection:
            self.db_connection.disconnect()
        event.accept()

