# -*- coding: utf-8 -*-
"""
测试配置文件
包含所有测试相关的配置参数
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent.parent


class TestConfig:
    """测试基础配置类"""
    
    # 基础URL配置
    BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:5000')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
    
    # 浏览器配置
    BROWSER = os.getenv('BROWSER', 'chrome').lower()
    HEADLESS = os.getenv('HEADLESS', 'False').lower() == 'true'
    
    # 等待时间配置
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', 10))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', 20))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', 30))
    
    # 路径配置
    REPORT_PATH = BASE_DIR / 'reports'
    SCREENSHOT_PATH = BASE_DIR / 'reports' / 'screenshots'
    TEST_DATA_PATH = BASE_DIR / 'tests' / 'data'
    LOG_PATH = BASE_DIR / 'logs'
    
    # 测试用户配置
    TEST_USER = {
        'email': os.getenv('TEST_USER_EMAIL', 'test@example.com'),
        'password': os.getenv('TEST_USER_PASSWORD', 'testpass123'),
        'username': 'testuser'
    }
    
    ADMIN_USER = {
        'email': os.getenv('ADMIN_EMAIL', 'admin@example.com'),
        'password': os.getenv('ADMIN_PASSWORD', 'adminpassword123'),
        'username': 'admin'
    }
    
    # API测试配置
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    RETRY_COUNT = int(os.getenv('RETRY_COUNT', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 1))
    
    # 数据库配置
    TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'sqlite:///test_database.db')
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        directories = [
            cls.REPORT_PATH,
            cls.SCREENSHOT_PATH,
            cls.TEST_DATA_PATH,
            cls.LOG_PATH
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_test_user(self):
        """获取测试用户信息"""
        return self.TEST_USER
    
    def get_admin_user(self):
        """获取管理员用户信息"""
        return self.ADMIN_USER


class SeleniumConfig(TestConfig):
    """Selenium测试配置"""
    
    # Chrome选项
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',  # 禁用图片加载以提高速度
    ]
    
    # Firefox选项
    FIREFOX_OPTIONS = [
        '--width=1920',
        '--height=1080',
    ]
    
    # Edge选项
    EDGE_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--window-size=1920,1080',
    ]
    
    @classmethod
    def get_chrome_options(cls):
        """获取Chrome浏览器选项"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        
        for option in cls.CHROME_OPTIONS:
            options.add_argument(option)
            
        if cls.HEADLESS:
            options.add_argument('--headless')
            
        return options
    
    @classmethod
    def get_firefox_options(cls):
        """获取Firefox浏览器选项"""
        from selenium.webdriver.firefox.options import Options
        options = Options()
        
        for option in cls.FIREFOX_OPTIONS:
            options.add_argument(option)
            
        if cls.HEADLESS:
            options.add_argument('--headless')
            
        return options


class PerformanceConfig(TestConfig):
    """性能测试配置"""
    
    # Locust配置
    LOCUST_HOST = os.getenv('LOCUST_HOST', 'http://localhost:5000')
    LOCUST_USERS = int(os.getenv('LOCUST_USERS', 10))
    LOCUST_SPAWN_RATE = int(os.getenv('LOCUST_SPAWN_RATE', 2))
    LOCUST_RUN_TIME = os.getenv('LOCUST_RUN_TIME', '60s')
    
    # 性能阈值
    RESPONSE_TIME_THRESHOLD = 2.0  # 秒
    ERROR_RATE_THRESHOLD = 0.05    # 5%
    THROUGHPUT_THRESHOLD = 100     # 每秒请求数


# 创建配置实例
test_config = TestConfig()
selenium_config = SeleniumConfig()
performance_config = PerformanceConfig()

# 确保目录存在
test_config.ensure_directories()