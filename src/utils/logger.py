# utils/logger.py
"""
日志工具类 - 统一日志输出格式
支持文件和控制台双输出，便于调试和追踪问题
"""
import logging
import os
from datetime import datetime

class Logger:
    """
    日志管理类（单例模式）
    确保整个项目使用统一的日志配置
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化日志配置"""
        if self._initialized:
            return
        
        self._initialized = True
        
        # 创建日志目录
        log_dir = "reports/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名（按日期）
        log_file = f"{log_dir}/test_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 创建logger
        self.logger = logging.getLogger('AutoTest')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(log_format, date_format))
            
            # 添加处理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """
        获取logger对象
        Returns:
            配置好的logger
        """
        return self.logger