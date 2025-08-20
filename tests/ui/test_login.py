#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录功能UI自动化测试
测试用户登录、注册、密码重置等功能
"""

import pytest
import time
from pages.login_page import LoginPage
from pages.home_page import HomePage
from config.test_config import TestConfig

config = TestConfig()

class TestLogin:
    """登录功能测试类"""
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.login_page = None
        self.home_page = None
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        pass
    
    @pytest.mark.smoke
    @pytest.mark.login
    def test_valid_login_with_test_user(self, driver):
        """测试使用测试用户有效登录"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 验证页面标题
        assert "登录" in driver.title
        
        # 验证登录表单元素存在
        assert self.login_page.is_username_input_visible()
        assert self.login_page.is_password_input_visible()
        assert self.login_page.is_login_button_visible()
        
        # 使用测试用户登录
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        
        # 等待页面跳转
        time.sleep(2)
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
        
        # 验证首页元素
        assert self.home_page.is_user_logged_in()
        
        # 验证用户名显示
        displayed_username = self.home_page.get_logged_in_username()
        assert test_user["username"] in displayed_username
    
    @pytest.mark.smoke
    @pytest.mark.login
    def test_valid_login_with_admin_user(self, driver):
        """测试使用管理员用户有效登录"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 使用管理员用户登录
        admin_user = config.get_admin_user()
        self.login_page.login(admin_user["username"], admin_user["password"])
        
        # 等待页面跳转
        time.sleep(2)
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
        assert self.home_page.is_user_logged_in()
        
        # 验证管理员用户名显示
        displayed_username = self.home_page.get_logged_in_username()
        assert admin_user["username"] in displayed_username
    
    @pytest.mark.login
    @pytest.mark.negative
    def test_invalid_login_wrong_password(self, driver):
        """测试错误密码登录失败"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 使用错误密码登录
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], "wrong_password")
        
        # 等待错误消息显示
        time.sleep(2)
        
        # 验证仍在登录页面
        assert "login" in driver.current_url
        
        # 验证错误消息显示
        error_message = self.login_page.get_error_message()
        assert error_message is not None
        assert "密码" in error_message or "错误" in error_message or "invalid" in error_message.lower()
    
    @pytest.mark.login
    @pytest.mark.negative
    def test_invalid_login_wrong_username(self, driver):
        """测试错误用户名登录失败"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 使用错误用户名登录
        self.login_page.login("nonexistent_user", "any_password")
        
        # 等待错误消息显示
        time.sleep(2)
        
        # 验证仍在登录页面
        assert "login" in driver.current_url
        
        # 验证错误消息显示
        error_message = self.login_page.get_error_message()
        assert error_message is not None
        assert "用户" in error_message or "不存在" in error_message or "invalid" in error_message.lower()
    
    @pytest.mark.login
    @pytest.mark.negative
    def test_empty_credentials_login(self, driver):
        """测试空凭据登录失败"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 尝试空凭据登录
        self.login_page.login("", "")
        
        # 等待验证消息显示
        time.sleep(1)
        
        # 验证仍在登录页面
        assert "login" in driver.current_url
        
        # 验证表单验证消息或错误消息
        error_message = self.login_page.get_error_message()
        if error_message:
            assert "必填" in error_message or "required" in error_message.lower() or "不能为空" in error_message
    
    @pytest.mark.login
    def test_remember_me_functionality(self, driver):
        """测试记住我功能"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 验证记住我复选框存在
        assert self.login_page.is_remember_me_checkbox_visible()
        
        # 勾选记住我
        self.login_page.check_remember_me()
        
        # 验证复选框被选中
        assert self.login_page.is_remember_me_checked()
        
        # 登录
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        
        # 等待登录完成
        time.sleep(2)
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
    
    @pytest.mark.login
    def test_quick_login_buttons(self, driver):
        """测试快速登录按钮"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 验证快速登录按钮存在
        assert self.login_page.is_test_user_button_visible()
        assert self.login_page.is_admin_button_visible()
        
        # 点击测试用户快速登录
        self.login_page.click_test_user_button()
        
        # 等待页面跳转
        time.sleep(2)
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
        assert self.home_page.is_user_logged_in()
    
    @pytest.mark.login
    def test_navigation_links(self, driver):
        """测试导航链接"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 验证注册链接存在
        if self.login_page.is_register_link_visible():
            # 点击注册链接
            self.login_page.click_register_link()
            
            # 验证跳转到注册页面
            time.sleep(1)
            assert "register" in driver.current_url or "注册" in driver.title
            
            # 返回登录页面
            driver.back()
            time.sleep(1)
        
        # 验证忘记密码链接存在
        if self.login_page.is_forgot_password_link_visible():
            # 点击忘记密码链接
            self.login_page.click_forgot_password_link()
            
            # 验证跳转到密码重置页面
            time.sleep(1)
            assert "forgot" in driver.current_url or "reset" in driver.current_url or "忘记" in driver.title
    
    @pytest.mark.login
    @pytest.mark.ui
    def test_login_form_validation(self, driver):
        """测试登录表单验证"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 测试用户名字段验证
        self.login_page.enter_username("")
        self.login_page.enter_password("test123")
        self.login_page.click_login_button()
        
        # 验证用户名验证消息
        time.sleep(1)
        assert "login" in driver.current_url  # 仍在登录页面
        
        # 测试密码字段验证
        self.login_page.enter_username("testuser")
        self.login_page.enter_password("")
        self.login_page.click_login_button()
        
        # 验证密码验证消息
        time.sleep(1)
        assert "login" in driver.current_url  # 仍在登录页面
    
    @pytest.mark.login
    @pytest.mark.security
    def test_sql_injection_protection(self, driver):
        """测试SQL注入防护"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 尝试SQL注入攻击
        sql_injection_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' OR 1=1--",
            "'; DROP TABLE users;--"
        ]
        
        for payload in sql_injection_payloads:
            # 清空输入框
            self.login_page.clear_username()
            self.login_page.clear_password()
            
            # 输入恶意载荷
            self.login_page.enter_username(payload)
            self.login_page.enter_password(payload)
            self.login_page.click_login_button()
            
            # 等待响应
            time.sleep(2)
            
            # 验证没有成功登录
            assert "login" in driver.current_url
            
            # 验证没有数据库错误信息泄露
            page_source = driver.page_source.lower()
            assert "sql" not in page_source
            assert "database" not in page_source
            assert "mysql" not in page_source
            assert "sqlite" not in page_source
    
    @pytest.mark.login
    @pytest.mark.performance
    def test_login_performance(self, driver):
        """测试登录性能"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 记录开始时间
        start_time = time.time()
        
        # 打开登录页面
        self.login_page.open()
        
        # 记录页面加载时间
        page_load_time = time.time() - start_time
        
        # 验证页面加载时间合理（小于5秒）
        assert page_load_time < 5.0, f"页面加载时间过长: {page_load_time:.2f}秒"
        
        # 记录登录开始时间
        login_start_time = time.time()
        
        # 执行登录
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        
        # 等待登录完成
        time.sleep(2)
        
        # 记录登录完成时间
        login_time = time.time() - login_start_time
        
        # 验证登录时间合理（小于10秒）
        assert login_time < 10.0, f"登录时间过长: {login_time:.2f}秒"
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
    
    @pytest.mark.login
    @pytest.mark.accessibility
    def test_login_accessibility(self, driver):
        """测试登录页面可访问性"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 验证表单标签
        username_input = self.login_page.find_element(self.login_page.USERNAME_INPUT)
        password_input = self.login_page.find_element(self.login_page.PASSWORD_INPUT)
        
        # 验证输入框有适当的标签或占位符
        assert (username_input.get_attribute("placeholder") or 
                username_input.get_attribute("aria-label") or
                username_input.get_attribute("title"))
        
        assert (password_input.get_attribute("placeholder") or 
                password_input.get_attribute("aria-label") or
                password_input.get_attribute("title"))
        
        # 验证按钮有适当的文本或标签
        login_button = self.login_page.find_element(self.login_page.LOGIN_BUTTON)
        assert (login_button.text or 
                login_button.get_attribute("aria-label") or
                login_button.get_attribute("title"))
    
    @pytest.mark.login
    @pytest.mark.responsive
    def test_login_responsive_design(self, driver):
        """测试登录页面响应式设计"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 测试不同屏幕尺寸
        screen_sizes = [
            (1920, 1080),  # 桌面
            (1024, 768),   # 平板横屏
            (768, 1024),   # 平板竖屏
            (375, 667),    # 手机
        ]
        
        for width, height in screen_sizes:
            # 设置窗口大小
            driver.set_window_size(width, height)
            time.sleep(1)
            
            # 验证关键元素仍然可见和可用
            assert self.login_page.is_username_input_visible()
            assert self.login_page.is_password_input_visible()
            assert self.login_page.is_login_button_visible()
            
            # 验证元素可以交互
            assert self.login_page.is_username_input_enabled()
            assert self.login_page.is_password_input_enabled()
            assert self.login_page.is_login_button_enabled()
        
        # 恢复默认窗口大小
        driver.maximize_window()
    
    @pytest.mark.login
    @pytest.mark.cross_browser
    def test_login_cross_browser_compatibility(self, driver):
        """测试登录跨浏览器兼容性"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 获取浏览器信息
        browser_name = driver.capabilities.get('browserName', 'unknown')
        browser_version = driver.capabilities.get('browserVersion', 'unknown')
        
        print(f"测试浏览器: {browser_name} {browser_version}")
        
        # 验证基本功能在所有浏览器中都能正常工作
        assert self.login_page.is_username_input_visible()
        assert self.login_page.is_password_input_visible()
        assert self.login_page.is_login_button_visible()
        
        # 执行登录测试
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        
        # 等待登录完成
        time.sleep(3)
        
        # 验证登录成功
        assert config.BASE_URL in driver.current_url
    
    @pytest.mark.login
    @pytest.mark.edge_case
    def test_login_edge_cases(self, driver):
        """测试登录边界情况"""
        # 初始化页面对象
        self.login_page = LoginPage(driver)
        
        # 打开登录页面
        self.login_page.open()
        
        # 测试特殊字符
        special_chars_username = "test@#$%^&*()_+"
        special_chars_password = "pass@#$%^&*()_+"
        
        self.login_page.login(special_chars_username, special_chars_password)
        time.sleep(2)
        
        # 验证处理特殊字符
        assert "login" in driver.current_url  # 应该仍在登录页面
        
        # 测试超长输入
        long_username = "a" * 1000
        long_password = "b" * 1000
        
        self.login_page.clear_username()
        self.login_page.clear_password()
        self.login_page.login(long_username, long_password)
        time.sleep(2)
        
        # 验证处理超长输入
        assert "login" in driver.current_url  # 应该仍在登录页面
        
        # 测试Unicode字符
        unicode_username = "测试用户名"
        unicode_password = "测试密码"
        
        self.login_page.clear_username()
        self.login_page.clear_password()
        self.login_page.login(unicode_username, unicode_password)
        time.sleep(2)
        
        # 验证处理Unicode字符
        assert "login" in driver.current_url  # 应该仍在登录页面