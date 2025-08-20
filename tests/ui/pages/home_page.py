#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页页面对象模型
封装首页的元素和操作
"""

from selenium.webdriver.common.by import By
from .base_page import BasePage
from config.test_config import TestConfig

config = TestConfig()

class HomePage(BasePage):
    """首页页面对象"""
    
    # 页面URL
    PAGE_URL = config.BASE_URL
    
    # 导航栏元素
    NAVBAR = (By.CSS_SELECTOR, ".navbar")
    BRAND_LOGO = (By.CSS_SELECTOR, ".navbar-brand")
    HOME_LINK = (By.LINK_TEXT, "首页")
    PRODUCTS_LINK = (By.LINK_TEXT, "商品")
    CART_LINK = (By.CSS_SELECTOR, ".cart-btn")
    CART_COUNT = (By.CSS_SELECTOR, ".cart-count")
    LOGIN_LINK = (By.LINK_TEXT, "登录")
    REGISTER_LINK = (By.LINK_TEXT, "注册")
    USER_DROPDOWN = (By.CSS_SELECTOR, ".dropdown-toggle")
    LOGOUT_LINK = (By.LINK_TEXT, "退出")
    
    # 搜索框
    SEARCH_BOX = (By.ID, "searchBox")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".search-btn")
    
    # 轮播图
    CAROUSEL = (By.ID, "heroCarousel")
    CAROUSEL_SLIDES = (By.CSS_SELECTOR, ".carousel-item")
    CAROUSEL_PREV = (By.CSS_SELECTOR, ".carousel-control-prev")
    CAROUSEL_NEXT = (By.CSS_SELECTOR, ".carousel-control-next")
    CAROUSEL_INDICATORS = (By.CSS_SELECTOR, ".carousel-indicators button")
    
    # 特色功能区
    FEATURES_SECTION = (By.CSS_SELECTOR, ".features")
    FEATURE_CARDS = (By.CSS_SELECTOR, ".feature-card")
    FEATURE_ICONS = (By.CSS_SELECTOR, ".feature-icon")
    FEATURE_TITLES = (By.CSS_SELECTOR, ".feature-card h4")
    FEATURE_DESCRIPTIONS = (By.CSS_SELECTOR, ".feature-card p")
    
    # 热门商品区
    POPULAR_PRODUCTS_SECTION = (By.CSS_SELECTOR, ".popular-products")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".product-card")
    PRODUCT_IMAGES = (By.CSS_SELECTOR, ".product-card img")
    PRODUCT_TITLES = (By.CSS_SELECTOR, ".product-card h5")
    PRODUCT_DESCRIPTIONS = (By.CSS_SELECTOR, ".product-card .text-muted")
    PRODUCT_PRICES = (By.CSS_SELECTOR, ".product-card .price")
    PRODUCT_STOCKS = (By.CSS_SELECTOR, ".product-card .stock")
    VIEW_DETAIL_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-primary")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".add-to-cart")
    
    # 统计数据区
    STATS_SECTION = (By.CSS_SELECTOR, ".stats")
    STAT_CARDS = (By.CSS_SELECTOR, ".stat-card")
    STAT_NUMBERS = (By.CSS_SELECTOR, ".stat-number")
    STAT_LABELS = (By.CSS_SELECTOR, ".stat-label")
    
    # 页脚
    FOOTER = (By.CSS_SELECTOR, "footer")
    FOOTER_LINKS = (By.CSS_SELECTOR, "footer a")
    COPYRIGHT = (By.CSS_SELECTOR, ".text-center p")
    
    # 提示消息
    ALERT_MESSAGE = (By.CSS_SELECTOR, ".alert")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open(self):
        """打开首页"""
        super().open(self.PAGE_URL)
        return self
    
    def click_brand_logo(self):
        """点击品牌Logo"""
        self.click(self.BRAND_LOGO)
        return self
    
    def click_home_link(self):
        """点击首页链接"""
        self.click(self.HOME_LINK)
        return self
    
    def click_products_link(self):
        """点击商品链接"""
        self.click(self.PRODUCTS_LINK)
        return self
    
    def click_cart_link(self):
        """点击购物车链接"""
        self.click(self.CART_LINK)
        return self
    
    def click_login_link(self):
        """点击登录链接"""
        self.click(self.LOGIN_LINK)
        return self
    
    def click_register_link(self):
        """点击注册链接"""
        self.click(self.REGISTER_LINK)
        return self
    
    def click_user_dropdown(self):
        """点击用户下拉菜单"""
        self.click(self.USER_DROPDOWN)
        return self
    
    def click_logout_link(self):
        """点击退出链接"""
        self.click(self.LOGOUT_LINK)
        return self
    
    def search_product(self, keyword):
        """搜索商品"""
        self.send_keys(self.SEARCH_BOX, keyword)
        self.click(self.SEARCH_BUTTON)
        return self
    
    def get_search_keyword(self):
        """获取搜索关键词"""
        return self.get_attribute(self.SEARCH_BOX, "value")
    
    def clear_search_box(self):
        """清空搜索框"""
        self.clear_input(self.SEARCH_BOX)
        return self
    
    def get_cart_count(self):
        """获取购物车商品数量"""
        if self.is_element_visible(self.CART_COUNT, timeout=3):
            return int(self.get_text(self.CART_COUNT))
        return 0
    
    def is_user_logged_in(self):
        """检查用户是否已登录"""
        return self.is_element_present(self.USER_DROPDOWN)
    
    def get_username_from_dropdown(self):
        """从下拉菜单获取用户名"""
        if self.is_user_logged_in():
            return self.get_text(self.USER_DROPDOWN)
        return None
    
    # 轮播图操作
    def click_carousel_next(self):
        """点击轮播图下一张"""
        self.click(self.CAROUSEL_NEXT)
        return self
    
    def click_carousel_prev(self):
        """点击轮播图上一张"""
        self.click(self.CAROUSEL_PREV)
        return self
    
    def click_carousel_indicator(self, index):
        """点击轮播图指示器"""
        indicators = self.find_elements(self.CAROUSEL_INDICATORS)
        if 0 <= index < len(indicators):
            indicators[index].click()
        return self
    
    def get_carousel_slides_count(self):
        """获取轮播图数量"""
        slides = self.find_elements(self.CAROUSEL_SLIDES)
        return len(slides)
    
    def get_active_carousel_slide_index(self):
        """获取当前活跃的轮播图索引"""
        slides = self.find_elements(self.CAROUSEL_SLIDES)
        for i, slide in enumerate(slides):
            if "active" in slide.get_attribute("class"):
                return i
        return -1
    
    # 特色功能区操作
    def get_features_count(self):
        """获取特色功能数量"""
        features = self.find_elements(self.FEATURE_CARDS)
        return len(features)
    
    def get_feature_info(self, index):
        """获取指定特色功能信息"""
        titles = self.find_elements(self.FEATURE_TITLES)
        descriptions = self.find_elements(self.FEATURE_DESCRIPTIONS)
        
        if 0 <= index < len(titles):
            return {
                "title": titles[index].text,
                "description": descriptions[index].text
            }
        return None
    
    def get_all_features_info(self):
        """获取所有特色功能信息"""
        features_count = self.get_features_count()
        features = []
        
        for i in range(features_count):
            feature_info = self.get_feature_info(i)
            if feature_info:
                features.append(feature_info)
        
        return features
    
    # 热门商品区操作
    def get_products_count(self):
        """获取热门商品数量"""
        products = self.find_elements(self.PRODUCT_CARDS)
        return len(products)
    
    def get_product_info(self, index):
        """获取指定商品信息"""
        titles = self.find_elements(self.PRODUCT_TITLES)
        descriptions = self.find_elements(self.PRODUCT_DESCRIPTIONS)
        prices = self.find_elements(self.PRODUCT_PRICES)
        stocks = self.find_elements(self.PRODUCT_STOCKS)
        
        if 0 <= index < len(titles):
            return {
                "title": titles[index].text,
                "description": descriptions[index].text,
                "price": prices[index].text,
                "stock": stocks[index].text
            }
        return None
    
    def get_all_products_info(self):
        """获取所有热门商品信息"""
        products_count = self.get_products_count()
        products = []
        
        for i in range(products_count):
            product_info = self.get_product_info(i)
            if product_info:
                products.append(product_info)
        
        return products
    
    def click_view_detail_button(self, index):
        """点击查看详情按钮"""
        buttons = self.find_elements(self.VIEW_DETAIL_BUTTONS)
        if 0 <= index < len(buttons):
            self.scroll_to_element(buttons[index])
            buttons[index].click()
        return self
    
    def click_add_to_cart_button(self, index):
        """点击添加到购物车按钮"""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if 0 <= index < len(buttons):
            self.scroll_to_element(buttons[index])
            buttons[index].click()
        return self
    
    def add_all_products_to_cart(self):
        """将所有商品添加到购物车"""
        products_count = self.get_products_count()
        for i in range(products_count):
            self.click_add_to_cart_button(i)
            # 等待一下避免操作过快
            import time
            time.sleep(0.5)
        return self
    
    # 统计数据区操作
    def get_stats_count(self):
        """获取统计数据数量"""
        stats = self.find_elements(self.STAT_CARDS)
        return len(stats)
    
    def get_stat_info(self, index):
        """获取指定统计数据信息"""
        numbers = self.find_elements(self.STAT_NUMBERS)
        labels = self.find_elements(self.STAT_LABELS)
        
        if 0 <= index < len(numbers):
            return {
                "number": numbers[index].text,
                "label": labels[index].text
            }
        return None
    
    def get_all_stats_info(self):
        """获取所有统计数据信息"""
        stats_count = self.get_stats_count()
        stats = []
        
        for i in range(stats_count):
            stat_info = self.get_stat_info(i)
            if stat_info:
                stats.append(stat_info)
        
        return stats
    
    def wait_for_stats_animation(self, timeout=10):
        """等待统计数据动画完成"""
        # 等待数字动画完成，通常数字会从0开始增长
        import time
        time.sleep(3)  # 等待动画完成
        return self
    
    # 消息提示操作
    def get_alert_message(self):
        """获取提示消息"""
        if self.is_element_visible(self.ALERT_MESSAGE, timeout=3):
            return self.get_text(self.ALERT_MESSAGE)
        return None
    
    def get_success_message(self):
        """获取成功消息"""
        if self.is_element_visible(self.SUCCESS_MESSAGE, timeout=3):
            return self.get_text(self.SUCCESS_MESSAGE)
        return None
    
    def get_error_message(self):
        """获取错误消息"""
        if self.is_element_visible(self.ERROR_MESSAGE, timeout=3):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def wait_for_success_message(self, timeout=None):
        """等待成功消息出现"""
        self.wait_for_element_visible(self.SUCCESS_MESSAGE, timeout)
        return self.get_success_message()
    
    def wait_for_error_message(self, timeout=None):
        """等待错误消息出现"""
        self.wait_for_element_visible(self.ERROR_MESSAGE, timeout)
        return self.get_error_message()
    
    # 页面验证方法
    def verify_homepage_elements(self):
        """验证首页所有元素是否存在"""
        elements_to_check = [
            ("navbar", self.NAVBAR),
            ("brand_logo", self.BRAND_LOGO),
            ("search_box", self.SEARCH_BOX),
            ("search_button", self.SEARCH_BUTTON),
            ("carousel", self.CAROUSEL),
            ("features_section", self.FEATURES_SECTION),
            ("popular_products_section", self.POPULAR_PRODUCTS_SECTION),
            ("stats_section", self.STATS_SECTION),
            ("footer", self.FOOTER)
        ]
        
        results = {}
        for element_name, locator in elements_to_check:
            results[element_name] = self.is_element_present(locator)
        
        return results
    
    def get_homepage_info(self):
        """获取首页完整信息"""
        return {
            "title": self.get_title(),
            "url": self.get_current_url(),
            "user_logged_in": self.is_user_logged_in(),
            "username": self.get_username_from_dropdown(),
            "cart_count": self.get_cart_count(),
            "carousel_slides_count": self.get_carousel_slides_count(),
            "features_count": self.get_features_count(),
            "products_count": self.get_products_count(),
            "stats_count": self.get_stats_count(),
            "elements_present": self.verify_homepage_elements()
        }
    
    def scroll_to_features_section(self):
        """滚动到特色功能区"""
        features_section = self.find_element(self.FEATURES_SECTION)
        self.scroll_to_element(features_section)
        return self
    
    def scroll_to_products_section(self):
        """滚动到热门商品区"""
        products_section = self.find_element(self.POPULAR_PRODUCTS_SECTION)
        self.scroll_to_element(products_section)
        return self
    
    def scroll_to_stats_section(self):
        """滚动到统计数据区"""
        stats_section = self.find_element(self.STATS_SECTION)
        self.scroll_to_element(stats_section)
        return self
    
    def scroll_to_footer(self):
        """滚动到页脚"""
        footer = self.find_element(self.FOOTER)
        self.scroll_to_element(footer)
        return self
    
    def perform_full_page_scroll(self):
        """执行完整页面滚动"""
        # 滚动到各个区域，模拟用户浏览行为
        self.scroll_to_features_section()
        import time
        time.sleep(1)
        
        self.scroll_to_products_section()
        time.sleep(1)
        
        self.scroll_to_stats_section()
        time.sleep(1)
        
        self.scroll_to_footer()
        time.sleep(1)
        
        # 回到顶部
        self.scroll_to_top()
        time.sleep(1)
        
        return self