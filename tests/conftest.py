# -*- coding: utf-8 -*-
"""
Pytest配置文件
提供全局的fixture和配置
"""

import pytest
import os
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.test_config import TestConfig

config = TestConfig()

def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome", 
        help="浏览器类型: chrome, firefox, edge"
    )
    parser.addoption(
        "--headless", 
        action="store_true", 
        default=False, 
        help="无头模式运行"
    )
    parser.addoption(
        "--base-url", 
        action="store", 
        default=config.BASE_URL, 
        help="测试基础URL"
    )
    parser.addoption(
        "--timeout", 
        action="store", 
        default=config.EXPLICIT_WAIT, 
        type=int,
        help="等待超时时间（秒）"
    )

@pytest.fixture(scope="session")
def browser_type(request):
    """获取浏览器类型"""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def headless_mode(request):
    """获取无头模式设置"""
    return request.config.getoption("--headless")

@pytest.fixture(scope="session")
def base_url(request):
    """获取基础URL"""
    return request.config.getoption("--base-url")

@pytest.fixture(scope="session")
def timeout(request):
    """获取超时时间"""
    return request.config.getoption("--timeout")

@pytest.fixture(scope="function")
def driver(browser_type, headless_mode, timeout):
    """创建WebDriver实例"""
    driver_instance = None
    
    try:
        if browser_type.lower() == "chrome":
            options = ChromeOptions()
            if headless_mode:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            
            # 获取Chrome驱动路径并修复路径问题
            driver_path = ChromeDriverManager().install()
            # 如果路径包含THIRD_PARTY_NOTICES，需要找到实际的chromedriver.exe
            if "THIRD_PARTY_NOTICES" in driver_path:
                import os
                driver_dir = os.path.dirname(driver_path)
                driver_path = os.path.join(driver_dir, "chromedriver.exe")
            
            service = ChromeService(driver_path)
            driver_instance = webdriver.Chrome(service=service, options=options)
            
        elif browser_type.lower() == "firefox":
            options = FirefoxOptions()
            if headless_mode:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            service = FirefoxService(GeckoDriverManager().install())
            driver_instance = webdriver.Firefox(service=service, options=options)
            
        elif browser_type.lower() == "edge":
            options = EdgeOptions()
            if headless_mode:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver_instance = webdriver.Edge(service=service, options=options)
            
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
        
        # 设置隐式等待
        driver_instance.implicitly_wait(timeout)
        
        # 最大化窗口（非无头模式）
        if not headless_mode:
            driver_instance.maximize_window()
        
        yield driver_instance
        
    except Exception as e:
        print(f"创建WebDriver失败: {e}")
        raise
    finally:
        if driver_instance:
            try:
                driver_instance.quit()
            except Exception as e:
                print(f"关闭WebDriver失败: {e}")

@pytest.fixture(scope="function")
def login_page(driver, base_url):
    """登录页面fixture"""
    sys.path.insert(0, str(Path(__file__).parent / 'ui'))
    from pages.login_page import LoginPage
    return LoginPage(driver, base_url)

@pytest.fixture(scope="function")
def home_page(driver, base_url):
    """首页fixture"""
    sys.path.insert(0, str(Path(__file__).parent / 'ui'))
    from pages.home_page import HomePage
    return HomePage(driver, base_url)

@pytest.fixture(scope="function")
def products_page(driver, base_url):
    """商品页面fixture"""
    sys.path.insert(0, str(Path(__file__).parent / 'ui'))
    from pages.products_page import ProductsPage
    return ProductsPage(driver, base_url)

@pytest.fixture(scope="function")
def cart_page(driver, base_url):
    """购物车页面fixture"""
    sys.path.insert(0, str(Path(__file__).parent / 'ui'))
    from pages.cart_page import CartPage
    return CartPage(driver, base_url)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 确保测试目录存在
    os.makedirs(config.REPORT_PATH, exist_ok=True)
    os.makedirs(config.SCREENSHOT_PATH, exist_ok=True)
    os.makedirs(config.LOG_PATH, exist_ok=True)
    
    yield
    
    # 测试后清理（如果需要）
    pass

@pytest.fixture(scope="function")
def screenshot_on_failure(request, driver):
    """测试失败时自动截图"""
    yield
    
    if request.node.rep_call.failed:
        # 生成截图文件名
        test_name = request.node.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"{test_name}_{timestamp}.png"
        screenshot_path = os.path.join(config.SCREENSHOT_PATH, screenshot_name)
        
        try:
            driver.save_screenshot(screenshot_path)
            print(f"\n截图已保存: {screenshot_path}")
        except Exception as e:
            print(f"\n保存截图失败: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """为每个测试创建报告对象"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# 测试数据fixtures
@pytest.fixture
def test_user():
    """测试用户数据"""
    return {
        'username': config.TEST_USER['username'],
        'password': config.TEST_USER['password']
    }

@pytest.fixture
def admin_user():
    """管理员用户数据"""
    return {
        'username': config.ADMIN_USER['username'],
        'password': config.ADMIN_USER['password']
    }

@pytest.fixture
def invalid_user():
    """无效用户数据"""
    return {
        'username': 'invalid_user',
        'password': 'invalid_password'
    }

# 测试标记
pytestmark = [
    pytest.mark.ui,
    pytest.mark.selenium
]