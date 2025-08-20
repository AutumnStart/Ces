#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面对象基类
提供所有页面对象的通用方法和属性
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time
import os
from datetime import datetime
from config.test_config import TestConfig

config = TestConfig()

class BasePage:
    """页面对象基类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
        self.actions = ActionChains(driver)
    
    def open(self, url):
        """打开指定URL"""
        self.driver.get(url)
        self.wait_for_page_load()
    
    def get_title(self):
        """获取页面标题"""
        return self.driver.title
    
    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def wait_for_page_load(self, timeout=None):
        """等待页面加载完成"""
        if timeout is None:
            timeout = config.PAGE_LOAD_TIMEOUT
        
        self.wait.until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    
    def find_element(self, locator, timeout=None):
        """查找单个元素"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"元素未找到: {locator}")
    
    def find_elements(self, locator, timeout=None):
        """查找多个元素"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []
    
    def wait_for_element_visible(self, locator, timeout=None):
        """等待元素可见"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"元素不可见: {locator}")
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """等待元素可点击"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            raise TimeoutException(f"元素不可点击: {locator}")
    
    def click(self, locator, timeout=None):
        """点击元素"""
        element = self.wait_for_element_clickable(locator, timeout)
        self.scroll_to_element(element)
        element.click()
        return element
    
    def send_keys(self, locator, text, clear=True, timeout=None):
        """向元素发送文本"""
        element = self.find_element(locator, timeout)
        self.scroll_to_element(element)
        
        if clear:
            element.clear()
        
        element.send_keys(text)
        return element
    
    def get_text(self, locator, timeout=None):
        """获取元素文本"""
        element = self.find_element(locator, timeout)
        return element.text
    
    def get_attribute(self, locator, attribute, timeout=None):
        """获取元素属性"""
        element = self.find_element(locator, timeout)
        return element.get_attribute(attribute)
    
    def is_element_present(self, locator):
        """检查元素是否存在"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def is_element_visible(self, locator, timeout=5):
        """检查元素是否可见"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(self, locator, timeout=5):
        """检查元素是否可点击"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def scroll_to_element(self, element):
        """滚动到指定元素"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
    
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0, 0);")
    
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def hover_over_element(self, locator, timeout=None):
        """鼠标悬停在元素上"""
        element = self.find_element(locator, timeout)
        self.actions.move_to_element(element).perform()
        return element
    
    def double_click(self, locator, timeout=None):
        """双击元素"""
        element = self.find_element(locator, timeout)
        self.actions.double_click(element).perform()
        return element
    
    def right_click(self, locator, timeout=None):
        """右键点击元素"""
        element = self.find_element(locator, timeout)
        self.actions.context_click(element).perform()
        return element
    
    def drag_and_drop(self, source_locator, target_locator, timeout=None):
        """拖拽元素"""
        source = self.find_element(source_locator, timeout)
        target = self.find_element(target_locator, timeout)
        self.actions.drag_and_drop(source, target).perform()
    
    def press_key(self, key):
        """按键"""
        self.actions.send_keys(key).perform()
    
    def press_enter(self):
        """按回车键"""
        self.press_key(Keys.ENTER)
    
    def press_escape(self):
        """按ESC键"""
        self.press_key(Keys.ESCAPE)
    
    def press_tab(self):
        """按Tab键"""
        self.press_key(Keys.TAB)
    
    def wait_for_text_in_element(self, locator, text, timeout=None):
        """等待元素包含指定文本"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            return True
        except TimeoutException:
            raise TimeoutException(f"元素中未找到文本 '{text}': {locator}")
    
    def wait_for_url_contains(self, url_part, timeout=None):
        """等待URL包含指定内容"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.url_contains(url_part)
            )
            return True
        except TimeoutException:
            raise TimeoutException(f"URL未包含 '{url_part}'")
    
    def wait_for_alert(self, timeout=None):
        """等待弹窗出现"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            return self.driver.switch_to.alert
        except TimeoutException:
            raise TimeoutException("弹窗未出现")
    
    def accept_alert(self, timeout=None):
        """接受弹窗"""
        alert = self.wait_for_alert(timeout)
        alert.accept()
    
    def dismiss_alert(self, timeout=None):
        """取消弹窗"""
        alert = self.wait_for_alert(timeout)
        alert.dismiss()
    
    def get_alert_text(self, timeout=None):
        """获取弹窗文本"""
        alert = self.wait_for_alert(timeout)
        return alert.text
    
    def switch_to_frame(self, frame_locator):
        """切换到iframe"""
        frame = self.find_element(frame_locator)
        self.driver.switch_to.frame(frame)
    
    def switch_to_default_content(self):
        """切换回主页面"""
        self.driver.switch_to.default_content()
    
    def switch_to_window(self, window_handle):
        """切换到指定窗口"""
        self.driver.switch_to.window(window_handle)
    
    def get_window_handles(self):
        """获取所有窗口句柄"""
        return self.driver.window_handles
    
    def close_current_window(self):
        """关闭当前窗口"""
        self.driver.close()
    
    def refresh_page(self):
        """刷新页面"""
        self.driver.refresh()
        self.wait_for_page_load()
    
    def go_back(self):
        """返回上一页"""
        self.driver.back()
        self.wait_for_page_load()
    
    def go_forward(self):
        """前进到下一页"""
        self.driver.forward()
        self.wait_for_page_load()
    
    def execute_script(self, script, *args):
        """执行JavaScript"""
        return self.driver.execute_script(script, *args)
    
    def take_screenshot(self, filename=None):
        """截图"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = config.SCREENSHOT_PATH / filename
        self.driver.save_screenshot(str(filepath))
        return str(filepath)
    
    def highlight_element(self, locator, timeout=None):
        """高亮显示元素（用于调试）"""
        element = self.find_element(locator, timeout)
        self.driver.execute_script(
            "arguments[0].style.border='3px solid red';", element
        )
        return element
    
    def remove_highlight(self, locator, timeout=None):
        """移除元素高亮"""
        element = self.find_element(locator, timeout)
        self.driver.execute_script(
            "arguments[0].style.border='';", element
        )
        return element
    
    def get_page_source(self):
        """获取页面源码"""
        return self.driver.page_source
    
    def get_cookies(self):
        """获取所有cookies"""
        return self.driver.get_cookies()
    
    def add_cookie(self, cookie_dict):
        """添加cookie"""
        self.driver.add_cookie(cookie_dict)
    
    def delete_cookie(self, name):
        """删除指定cookie"""
        self.driver.delete_cookie(name)
    
    def delete_all_cookies(self):
        """删除所有cookies"""
        self.driver.delete_all_cookies()
    
    def set_window_size(self, width, height):
        """设置窗口大小"""
        self.driver.set_window_size(width, height)
    
    def maximize_window(self):
        """最大化窗口"""
        self.driver.maximize_window()
    
    def minimize_window(self):
        """最小化窗口"""
        self.driver.minimize_window()
    
    def get_window_size(self):
        """获取窗口大小"""
        return self.driver.get_window_size()
    
    def get_window_position(self):
        """获取窗口位置"""
        return self.driver.get_window_position()
    
    def set_window_position(self, x, y):
        """设置窗口位置"""
        self.driver.set_window_position(x, y)
    
    def wait_and_click(self, locator, timeout=None):
        """等待并点击元素"""
        return self.click(locator, timeout)
    
    def wait_and_send_keys(self, locator, text, clear=True, timeout=None):
        """等待并发送文本"""
        return self.send_keys(locator, text, clear, timeout)
    
    def wait_and_get_text(self, locator, timeout=None):
        """等待并获取文本"""
        return self.get_text(locator, timeout)
    
    def select_dropdown_by_text(self, locator, text, timeout=None):
        """通过文本选择下拉框选项"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator, timeout)
        select = Select(element)
        select.select_by_visible_text(text)
    
    def select_dropdown_by_value(self, locator, value, timeout=None):
        """通过值选择下拉框选项"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator, timeout)
        select = Select(element)
        select.select_by_value(value)
    
    def select_dropdown_by_index(self, locator, index, timeout=None):
        """通过索引选择下拉框选项"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator, timeout)
        select = Select(element)
        select.select_by_index(index)
    
    def get_selected_dropdown_text(self, locator, timeout=None):
        """获取下拉框选中的文本"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator, timeout)
        select = Select(element)
        return select.first_selected_option.text
    
    def upload_file(self, locator, file_path, timeout=None):
        """上传文件"""
        element = self.find_element(locator, timeout)
        element.send_keys(file_path)
    
    def clear_input(self, locator, timeout=None):
        """清空输入框"""
        element = self.find_element(locator, timeout)
        element.clear()
    
    def get_element_size(self, locator, timeout=None):
        """获取元素大小"""
        element = self.find_element(locator, timeout)
        return element.size
    
    def get_element_location(self, locator, timeout=None):
        """获取元素位置"""
        element = self.find_element(locator, timeout)
        return element.location
    
    def is_element_enabled(self, locator, timeout=None):
        """检查元素是否启用"""
        element = self.find_element(locator, timeout)
        return element.is_enabled()
    
    def is_element_selected(self, locator, timeout=None):
        """检查元素是否选中"""
        element = self.find_element(locator, timeout)
        return element.is_selected()
    
    def wait_for_element_to_disappear(self, locator, timeout=None):
        """等待元素消失"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_number_of_windows(self, number, timeout=None):
        """等待窗口数量"""
        if timeout is None:
            timeout = config.EXPLICIT_WAIT
        
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(driver.window_handles) == number
            )
            return True
        except TimeoutException:
            return False