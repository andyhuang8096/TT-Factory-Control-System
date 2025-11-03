"""配置管理模块。

负责读取和写入 INI 格式的配置文件。
"""

import configparser
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类。
    
    负责管理应用程序的配置文件，支持读取和写入 INI 格式的配置。
    """
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """初始化配置管理器。
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        if config_path is None:
            # 默认配置文件路径（项目根目录的 config/app.ini）
            # __file__ 是 src/core/config/config_manager.py
            # parent.parent.parent.parent 是项目根目录
            base_dir = Path(__file__).parent.parent.parent.parent
            config_path = str(base_dir / "config" / "app.ini")
        
        self.config_path = Path(config_path)
        # 禁用插值以避免密码中的特殊字符导致解析错误
        self.config = configparser.ConfigParser(interpolation=None)
        self._config_data: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self) -> bool:
        """加载配置文件。
        
        Returns:
            加载成功返回 True，失败返回 False
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"配置文件不存在: {self.config_path}")
                return False
            
            self.config.read(self.config_path, encoding='utf-8')
            self._config_data = {section: dict(self.config[section]) 
                                for section in self.config.sections()}
            logger.info(f"配置文件加载成功: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}", exc_info=True)
            return False
    
    def save_config(self) -> bool:
        """保存配置文件。
        
        Returns:
            保存成功返回 True，失败返回 False
        """
        try:
            # 确保配置目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 将配置数据写入 configparser
            for section, options in self._config_data.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                for key, value in options.items():
                    self.config.set(section, key, str(value))
            
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            logger.info(f"配置文件保存成功: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}", exc_info=True)
            return False
    
    def get(self, section: str, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值。
        
        Args:
            section: 配置节名称
            key: 配置键名称
            default: 默认值
        
        Returns:
            配置值，如果不存在则返回默认值
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def set(self, section: str, key: str, value: str) -> None:
        """设置配置值。
        
        Args:
            section: 配置节名称
            key: 配置键名称
            value: 配置值
        """
        if section not in self._config_data:
            self._config_data[section] = {}
        self._config_data[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, str]:
        """获取整个配置节。
        
        Args:
            section: 配置节名称
        
        Returns:
            配置节的字典，如果不存在则返回空字典
        """
        try:
            return dict(self.config[section])
        except configparser.NoSectionError:
            return {}
    
    def get_database_config(self) -> Dict[str, str]:
        """获取数据库配置。
        
        Returns:
            数据库配置字典，包含 server, database, login, password 等
        """
        return self.get_section("Database")
    
    def get_import_config(self) -> Dict[str, str]:
        """获取导入配置。
        
        Returns:
            导入配置字典
        """
        return self.get_section("Import")
    
    def get_report_config(self) -> Dict[str, str]:
        """获取报表配置。
        
        Returns:
            报表配置字典
        """
        return self.get_section("Report")
    
    def get_options_config(self) -> Dict[str, str]:
        """获取选项配置。
        
        Returns:
            选项配置字典
        """
        return self.get_section("Options")

