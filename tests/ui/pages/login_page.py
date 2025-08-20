#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录页面对象模型
封装登录页面的元素和操作
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from config.test_config import TestConfig

config = TestConfig()

class LoginPage(BasePage):
    """登录页面对象"""
    
    # 页面URL
    PAGE_URL = f"{config.BASE_URL}/login"
    
    # 元素定位器
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    REGISTER_LINK = (By.LINK_TEXT, "立即注册")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "忘记密码？")
    
    # 测试用户按钮
    TEST_USER_BUTTON = (By.ID, "fillTestUser")
    ADMIN_USER_BUTTON = (By.ID, "fillAdminUser")
    
    # 密码显示/隐藏
    TOGGLE_PASSWORD_BUTTON = (By.CSS_SELECTOR, ".toggle-password")
    
    # 错误消息
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
    
    # 表单验证消息
    USERNAME_ERROR = (By.CSS_SELECTOR, "#username + .invalid-feedback")
    PASSWORD_ERROR = (By.CSS_SELECTOR, "#password + .invalid-feedback")
    
    # 页面标题和标识
    PAGE_TITLE = (By.TAG_NAME, "title")
    LOGIN_FORM = (By.ID, "loginForm")
    PAGE_HEADING = (By.CSS_SELECTOR, "h2")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open(self):
        """打开登录页面"""
        super().open(self.PAGE_URL)
        return self
    
    def enter_username(self, username):
        """输入用户名"""
        self.send_keys(self.USERNAME_INPUT, username)
        return self
    
    def enter_password(self, password):
        """输入密码"""
        self.send_keys(self.PASSWORD_INPUT, password)
        return self
    
    def click_remember_me(self):
        """点击记住我复选框"""
        self.click(self.REMEMBER_ME_CHECKBOX)
        return self
    
    def click_login_button(self):
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON)
        return self
    
    def click_register_link(self):
        """点击注册链接"""
        self.click(self.REGISTER_LINK)
        return self
    
    def click_forgot_password_link(self):
        """点击忘记密码链接"""
        self.click(self.FORGOT_PASSWORD_LINK)
        return self
    
    def click_test_user_button(self):
        """点击测试用户按钮"""
        self.click(self.TEST_USER_BUTTON)
        return self
    
    def click_admin_user_button(self):
        """点击管理员用户按钮"""
        self.click(self.ADMIN_USER_BUTTON)
        return self
    
    def toggle_password_visibility(self):
        """切换密码显示/隐藏"""
        self.click(self.TOGGLE_PASSWORD_BUTTON)
        return self
    
    def login(self, username, password, remember_me=False):
        """执行登录操作"""
        self.enter_username(username)
        self.enter_password(password)
        
        if remember_me:
            self.click_remember_me()
        
        self.click_login_button()
        return self
    
    def login_with_test_user(self):
        """使用测试用户登录"""
        self.click_test_user_button()
        self.click_login_button()
        return self
    
    def login_with_admin_user(self):
        """使用管理员用户登录"""
        self.click_admin_user_button()
        self.click_login_button()
        return self
    
    def get_username_value(self):
        """获取用户名输入框的值"""
        return self.get_attribute(self.USERNAME_INPUT, "value")
    
    def get_password_value(self):
        """获取密码输入框的值"""
        return self.get_attribute(self.PASSWORD_INPUT, "value")
    
    def is_remember_me_checked(self):
        """检查记住我是否选中"""
        return self.is_element_selected(self.REMEMBER_ME_CHECKBOX)
    
    def is_password_visible(self):
        """检查密码是否可见"""
        password_type = self.get_attribute(self.PASSWORD_INPUT, "type")
        return password_type == "text"
    
    def get_error_message(self):
        """获取错误消息"""
        if self.is_element_visible(self.ERROR_MESSAGE, timeout=3):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def get_success_message(self):
        """获取成功消息"""
        if self.is_element_visible(self.SUCCESS_MESSAGE, timeout=3):
            return self.get_text(self.SUCCESS_MESSAGE)
        return None
    
    def get_username_error(self):
        """获取用户名验证错误消息"""
        if self.is_element_visible(self.USERNAME_ERROR, timeout=3):
            return self.get_text(self.USERNAME_ERROR)
        return None
    
    def get_password_error(self):
        """获取密码验证错误消息"""
        if self.is_element_visible(self.PASSWORD_ERROR, timeout=3):
            return self.get_text(self.PASSWORD_ERROR)
        return None
    
    def is_login_form_present(self):
        """检查登录表单是否存在"""
        return self.is_element_present(self.LOGIN_FORM)
    
    def is_login_button_enabled(self):
        """检查登录按钮是否可用"""
        return self.is_element_enabled(self.LOGIN_BUTTON)
    
    def is_username_input_visible(self):
        """检查用户名输入框是否可见"""
        return self.is_element_visible(self.USERNAME_INPUT)
    
    def is_password_input_visible(self):
        """检查密码输入框是否可见"""
        return self.is_element_visible(self.PASSWORD_INPUT)
    
    def is_login_button_visible(self):
        """检查登录按钮是否可见"""
        return self.is_element_visible(self.LOGIN_BUTTON)
    
    def clear_username(self):
        """清空用户名输入框"""
        self.clear_input(self.USERNAME_INPUT)
        return self
    
    def clear_password(self):
        """清空密码输入框"""
        self.clear_input(self.PASSWORD_INPUT)
        return self
    
    def clear_form(self):
        """清空整个表单"""
        self.clear_username()
        self.clear_password()
        return self
    
    def get_page_heading(self):
        """获取页面标题"""
        return self.get_text(self.PAGE_HEADING)
    
    def wait_for_login_form(self, timeout=None):
        """等待登录表单加载"""
        self.wait_for_element_visible(self.LOGIN_FORM, timeout)
        return self
    
    def wait_for_redirect_after_login(self, timeout=None):
        """等待登录后重定向"""
        # 等待URL不再是登录页面
        self.wait.until(
            lambda driver: self.PAGE_URL not in driver.current_url
        )
        return self
    
    def submit_form_by_enter(self):
        """通过回车键提交表单"""
        password_field = self.find_element(self.PASSWORD_INPUT)
        password_field.send_keys(self.driver.keys.ENTER)
        return self
    
    def focus_username_field(self):
        """聚焦到用户名输入框"""
        username_field = self.find_element(self.USERNAME_INPUT)
        username_field.click()
        return self
    
    def focus_password_field(self):
        """聚焦到密码输入框"""
        password_field = self.find_element(self.PASSWORD_INPUT)
        password_field.click()
        return self
    
    def tab_to_next_field(self):
        """Tab键切换到下一个字段"""
        self.press_tab()
        return self
    
    def get_username_placeholder(self):
        """获取用户名输入框占位符"""
        return self.get_attribute(self.USERNAME_INPUT, "placeholder")
    
    def get_password_placeholder(self):
        """获取密码输入框占位符"""
        return self.get_attribute(self.PASSWORD_INPUT, "placeholder")
    
    def is_username_field_focused(self):
        """检查用户名输入框是否聚焦"""
        active_element = self.driver.switch_to.active_element
        username_element = self.find_element(self.USERNAME_INPUT)
        return active_element == username_element
    
    def is_password_field_focused(self):
        """检查密码输入框是否聚焦"""
        active_element = self.driver.switch_to.active_element
        password_element = self.find_element(self.PASSWORD_INPUT)
        return active_element == password_element
    
    def get_form_validation_state(self):
        """获取表单验证状态"""
        username_valid = "is-valid" in self.get_attribute(self.USERNAME_INPUT, "class")
        username_invalid = "is-invalid" in self.get_attribute(self.USERNAME_INPUT, "class")
        password_valid = "is-valid" in self.get_attribute(self.PASSWORD_INPUT, "class")
        password_invalid = "is-invalid" in self.get_attribute(self.PASSWORD_INPUT, "class")
        
        return {
            "username_valid": username_valid,
            "username_invalid": username_invalid,
            "password_valid": password_valid,
            "password_invalid": password_invalid
        }
    
    def wait_for_error_message(self, timeout=None):
        """等待错误消息出现"""
        self.wait_for_element_visible(self.ERROR_MESSAGE, timeout)
        return self.get_error_message()
    
    def wait_for_success_message(self, timeout=None):
        """等待成功消息出现"""
        self.wait_for_element_visible(self.SUCCESS_MESSAGE, timeout)
        return self.get_success_message()
    
    def perform_invalid_login_attempts(self, attempts):
        """执行多次无效登录尝试"""
        results = []
        for i, (username, password) in enumerate(attempts):
            self.clear_form()
            self.login(username, password)
            
            # 等待响应
            import time
            time.sleep(1)
            
            error_msg = self.get_error_message()
            results.append({
                "attempt": i + 1,
                "username": username,
                "password": password,
                "error_message": error_msg,
                "current_url": self.get_current_url()
            })
        
        return results
    
    def verify_login_page_elements(self):
        """验证登录页面所有元素是否存在"""
        elements_to_check = [
            ("username_input", self.USERNAME_INPUT),
            ("password_input", self.PASSWORD_INPUT),
            ("remember_me_checkbox", self.REMEMBER_ME_CHECKBOX),
            ("login_button", self.LOGIN_BUTTON),
            ("register_link", self.REGISTER_LINK),
            ("test_user_button", self.TEST_USER_BUTTON),
            ("admin_user_button", self.ADMIN_USER_BUTTON),
            ("toggle_password_button", self.TOGGLE_PASSWORD_BUTTON)
        ]
        
        results = {}
        for element_name, locator in elements_to_check:
            results[element_name] = self.is_element_present(locator)
        
        return results
    
    def get_login_page_info(self):
        """获取登录页面信息"""
        return {
            "title": self.get_title(),
            "url": self.get_current_url(),
            "heading": self.get_page_heading(),
            "username_placeholder": self.get_username_placeholder(),
            "password_placeholder": self.get_password_placeholder(),
            "elements_present": self.verify_login_page_elements()
        }
    
    def is_remember_me_checkbox_visible(self):
        """检查记住我复选框是否可见"""
        return self.is_element_visible(self.REMEMBER_ME_CHECKBOX)
    
    def is_test_user_button_visible(self):
        """检查测试用户按钮是否可见"""
        return self.is_element_visible(self.TEST_USER_BUTTON)
    
    def is_register_link_visible(self):
        """检查注册链接是否可见"""
        return self.is_element_visible(self.REGISTER_LINK)
    
    def is_username_input_enabled(self):
        """检查用户名输入框是否启用"""
        return self.is_element_enabled(self.USERNAME_INPUT)
    
    def is_password_input_enabled(self):
        """检查密码输入框是否启用"""
        return self.is_element_enabled(self.PASSWORD_INPUT)
    
    def is_forgot_password_link_visible(self):
        """检查忘记密码链接是否可见"""
        return self.is_element_visible(self.FORGOT_PASSWORD_LINK)