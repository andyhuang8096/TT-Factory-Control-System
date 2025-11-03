"""应用主入口文件。

这是应用程序的入口点，负责初始化应用并启动主窗口。
"""

import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.utils.logger import setup_logging
from src.core.config.config_manager import ConfigManager


def main() -> int:
    """主函数。
    
    Returns:
        应用程序退出码
    """
    # 设置日志
    setup_logging()
    
    # 创建 Qt 应用
    app = QApplication(sys.argv)
    app.setApplicationName("EasyPPID 数据库管理系统")
    app.setOrganizationName("TG Electronic")
    
    # 加载配置
    try:
        config = ConfigManager()
        config.load_config()
    except Exception as e:
        print(f"配置加载失败: {e}")
        return 1
    
    # 创建主窗口
    try:
        main_window = MainWindow(config)
        main_window.show()
        
        # 运行应用
        return app.exec()
    except Exception as e:
        print(f"应用启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

