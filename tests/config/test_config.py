#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置管理
用于管理不同环境的测试配置
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DatabaseConfig:
    """
    数据库配置
    """
    host: str = "localhost"
    port: int = 5432
    database: str = "test_db"
    username: str = "test_user"
    password: str = "test_password"
    driver: str = "sqlite"  # sqlite, postgresql, mysql
    connection_string: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class WebConfig:
    """
    Web应用配置
    """
    base_url: str = "http://localhost:5000"
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = False
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                "User-Agent": "TestAutomation/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }


@dataclass
class SeleniumConfig:
    """
    Selenium配置
    """
    browser: str = "chrome"  # chrome, firefox, edge, safari
    headless: bool = True
    window_size: str = "1920,1080"
    implicit_wait: int = 10
    explicit_wait: int = 30
    page_load_timeout: int = 30
    script_timeout: int = 30
    download_dir: Optional[str] = None
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    chrome_options: list = None
    firefox_options: list = None
    
    def __post_init__(self):
        if self.chrome_options is None:
            self.chrome_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-web-security",
                "--allow-running-insecure-content"
            ]
        
        if self.firefox_options is None:
            self.firefox_options = [
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]


@dataclass
class APIConfig:
    """
    API测试配置
    """
    base_url: str = "http://localhost:5000/api"
    version: str = "v1"
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    auth_type: str = "none"  # none, basic, bearer, api_key
    auth_token: Optional[str] = None
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    verify_ssl: bool = False
    default_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.default_headers is None:
            self.default_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "API-Test/1.0"
            }


@dataclass
class PerformanceConfig:
    """
    性能测试配置
    """
    max_response_time: float = 2.0  # 秒
    target_response_time: float = 1.0  # 秒
    concurrent_users: int = 10
    test_duration: int = 60  # 秒
    ramp_up_time: int = 10  # 秒
    think_time: float = 1.0  # 秒
    success_rate_threshold: float = 0.95  # 95%
    error_rate_threshold: float = 0.05  # 5%
    cpu_threshold: float = 80.0  # %
    memory_threshold: float = 80.0  # %
    disk_threshold: float = 80.0  # %


@dataclass
class SecurityConfig:
    """
    安全测试配置
    """
    scan_timeout: int = 300  # 秒
    max_scan_depth: int = 3
    excluded_paths: list = None
    included_paths: list = None
    custom_headers: Dict[str, str] = None
    authentication_required: bool = False
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    
    def __post_init__(self):
        if self.excluded_paths is None:
            self.excluded_paths = [
                "/admin",
                "/static",
                "/assets",
                "/.git",
                "/node_modules"
            ]
        
        if self.included_paths is None:
            self.included_paths = [
                "/",
                "/api",
                "/login",
                "/register"
            ]
        
        if self.custom_headers is None:
            self.custom_headers = {}


@dataclass
class ReportConfig:
    """
    报告配置
    """
    output_dir: str = "reports"
    format: str = "html"  # html, json, xml, pdf
    include_screenshots: bool = True
    include_logs: bool = True
    include_performance_metrics: bool = True
    include_coverage: bool = False
    template: Optional[str] = None
    title: str = "测试报告"
    description: str = "自动化测试执行报告"
    author: str = "测试团队"
    

@dataclass
class TestConfig:
    """
    主测试配置类
    """
    environment: str = "test"  # test, staging, production
    debug: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_file: Optional[str] = None
    parallel_execution: bool = False
    max_workers: int = 4
    test_data_file: Optional[str] = None
    cleanup_after_test: bool = True
    
    # 子配置
    database: DatabaseConfig = None
    web: WebConfig = None
    selenium: SeleniumConfig = None
    api: APIConfig = None
    performance: PerformanceConfig = None
    security: SecurityConfig = None
    report: ReportConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.web is None:
            self.web = WebConfig()
        if self.selenium is None:
            self.selenium = SeleniumConfig()
        if self.api is None:
            self.api = APIConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.report is None:
            self.report = ReportConfig()


class ConfigManager:
    """
    配置管理器
    """
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config_cache = {}
    
    def load_config(self, environment: str = None) -> TestConfig:
        """
        加载指定环境的配置
        """
        if environment is None:
            environment = os.getenv('TEST_ENV', 'test')
        
        # 检查缓存
        if environment in self._config_cache:
            return self._config_cache[environment]
        
        config_file = self.config_dir / f"{environment}.json"
        
        if config_file.exists():
            # 从文件加载配置
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            config = self._dict_to_config(config_data)
        else:
            # 使用默认配置
            config = self._get_default_config(environment)
            # 保存默认配置到文件
            self.save_config(config, environment)
        
        # 应用环境变量覆盖
        config = self._apply_env_overrides(config)
        
        # 缓存配置
        self._config_cache[environment] = config
        
        return config
    
    def save_config(self, config: TestConfig, environment: str = None):
        """
        保存配置到文件
        """
        if environment is None:
            environment = config.environment
        
        config_file = self.config_dir / f"{environment}.json"
        config_dict = self._config_to_dict(config)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        print(f"配置已保存到: {config_file}")
    
    def _get_default_config(self, environment: str) -> TestConfig:
        """
        获取默认配置
        """
        if environment == "production":
            return TestConfig(
                environment=environment,
                debug=False,
                log_level="WARNING",
                parallel_execution=True,
                max_workers=8,
                cleanup_after_test=False,
                database=DatabaseConfig(
                    host="prod-db.example.com",
                    database="prod_db",
                    echo=False
                ),
                web=WebConfig(
                    base_url="https://prod.example.com",
                    verify_ssl=True
                ),
                selenium=SeleniumConfig(
                    headless=True,
                    implicit_wait=5,
                    explicit_wait=15
                ),
                api=APIConfig(
                    base_url="https://api.prod.example.com",
                    verify_ssl=True
                ),
                performance=PerformanceConfig(
                    max_response_time=1.0,
                    target_response_time=0.5,
                    concurrent_users=50,
                    test_duration=300
                )
            )
        
        elif environment == "staging":
            return TestConfig(
                environment=environment,
                debug=False,
                log_level="INFO",
                parallel_execution=True,
                max_workers=4,
                database=DatabaseConfig(
                    host="staging-db.example.com",
                    database="staging_db"
                ),
                web=WebConfig(
                    base_url="https://staging.example.com"
                ),
                api=APIConfig(
                    base_url="https://api.staging.example.com"
                ),
                performance=PerformanceConfig(
                    concurrent_users=20,
                    test_duration=120
                )
            )
        
        else:  # test environment
            return TestConfig(
                environment=environment,
                debug=True,
                log_level="DEBUG",
                parallel_execution=False,
                max_workers=2,
                database=DatabaseConfig(
                    driver="sqlite",
                    connection_string="sqlite:///test.db"
                ),
                web=WebConfig(
                    base_url="http://localhost:5000"
                ),
                selenium=SeleniumConfig(
                    headless=False,  # 测试环境显示浏览器
                    implicit_wait=10
                ),
                api=APIConfig(
                    base_url="http://localhost:5000/api"
                )
            )
    
    def _apply_env_overrides(self, config: TestConfig) -> TestConfig:
        """
        应用环境变量覆盖
        """
        # 主配置覆盖
        if os.getenv('TEST_DEBUG'):
            config.debug = os.getenv('TEST_DEBUG').lower() == 'true'
        
        if os.getenv('TEST_LOG_LEVEL'):
            config.log_level = os.getenv('TEST_LOG_LEVEL')
        
        if os.getenv('TEST_PARALLEL'):
            config.parallel_execution = os.getenv('TEST_PARALLEL').lower() == 'true'
        
        # Web配置覆盖
        if os.getenv('TEST_BASE_URL'):
            config.web.base_url = os.getenv('TEST_BASE_URL')
        
        if os.getenv('TEST_TIMEOUT'):
            config.web.timeout = int(os.getenv('TEST_TIMEOUT'))
        
        # API配置覆盖
        if os.getenv('API_BASE_URL'):
            config.api.base_url = os.getenv('API_BASE_URL')
        
        if os.getenv('API_TOKEN'):
            config.api.auth_token = os.getenv('API_TOKEN')
            config.api.auth_type = 'bearer'
        
        # 数据库配置覆盖
        if os.getenv('DB_HOST'):
            config.database.host = os.getenv('DB_HOST')
        
        if os.getenv('DB_PORT'):
            config.database.port = int(os.getenv('DB_PORT'))
        
        if os.getenv('DB_NAME'):
            config.database.database = os.getenv('DB_NAME')
        
        if os.getenv('DB_USER'):
            config.database.username = os.getenv('DB_USER')
        
        if os.getenv('DB_PASSWORD'):
            config.database.password = os.getenv('DB_PASSWORD')
        
        # Selenium配置覆盖
        if os.getenv('SELENIUM_BROWSER'):
            config.selenium.browser = os.getenv('SELENIUM_BROWSER')
        
        if os.getenv('SELENIUM_HEADLESS'):
            config.selenium.headless = os.getenv('SELENIUM_HEADLESS').lower() == 'true'
        
        return config
    
    def _config_to_dict(self, config: TestConfig) -> Dict[str, Any]:
        """
        将配置对象转换为字典
        """
        return asdict(config)
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> TestConfig:
        """
        将字典转换为配置对象
        """
        # 处理嵌套配置
        if 'database' in config_dict:
            config_dict['database'] = DatabaseConfig(**config_dict['database'])
        
        if 'web' in config_dict:
            config_dict['web'] = WebConfig(**config_dict['web'])
        
        if 'selenium' in config_dict:
            config_dict['selenium'] = SeleniumConfig(**config_dict['selenium'])
        
        if 'api' in config_dict:
            config_dict['api'] = APIConfig(**config_dict['api'])
        
        if 'performance' in config_dict:
            config_dict['performance'] = PerformanceConfig(**config_dict['performance'])
        
        if 'security' in config_dict:
            config_dict['security'] = SecurityConfig(**config_dict['security'])
        
        if 'report' in config_dict:
            config_dict['report'] = ReportConfig(**config_dict['report'])
        
        return TestConfig(**config_dict)
    
    def get_database_url(self, environment: str = None) -> str:
        """
        获取数据库连接URL
        """
        config = self.load_config(environment)
        db_config = config.database
        
        if db_config.connection_string:
            return db_config.connection_string
        
        if db_config.driver == 'sqlite':
            return f"sqlite:///{db_config.database}"
        elif db_config.driver == 'postgresql':
            return f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        elif db_config.driver == 'mysql':
            return f"mysql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
        else:
            raise ValueError(f"不支持的数据库驱动: {db_config.driver}")
    
    def create_sample_configs(self):
        """
        创建示例配置文件
        """
        environments = ['test', 'staging', 'production']
        
        for env in environments:
            config = self._get_default_config(env)
            self.save_config(config, env)
        
        print(f"示例配置文件已创建在: {self.config_dir}")


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config(environment: str = None) -> TestConfig:
    """
    获取配置的便捷函数
    """
    return config_manager.load_config(environment)


def get_database_url(environment: str = None) -> str:
    """
    获取数据库URL的便捷函数
    """
    return config_manager.get_database_url(environment)


if __name__ == '__main__':
    # 创建示例配置文件
    config_manager.create_sample_configs()
    
    # 测试配置加载
    test_config = get_config('test')
    print(f"测试环境配置: {test_config.web.base_url}")
    
    staging_config = get_config('staging')
    print(f"预发布环境配置: {staging_config.web.base_url}")
    
    prod_config = get_config('production')
    print(f"生产环境配置: {prod_config.web.base_url}")