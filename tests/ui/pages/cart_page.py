#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购物车页面对象模型
封装购物车页面的元素和操作
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage
from config.test_config import TestConfig

config = TestConfig()

class CartPage(BasePage):
    """购物车页面对象"""
    
    # 页面URL
    PAGE_URL = f"{config.BASE_URL}/cart"
    
    # 页面标题
    PAGE_TITLE = (By.CSS_SELECTOR, ".page-title")
    
    # 购物车商品列表
    CART_ITEMS = (By.CSS_SELECTOR, ".cart-item")
    ITEM_CHECKBOXES = (By.CSS_SELECTOR, ".item-checkbox")
    ITEM_IMAGES = (By.CSS_SELECTOR, ".item-image img")
    ITEM_TITLES = (By.CSS_SELECTOR, ".item-title")
    ITEM_DESCRIPTIONS = (By.CSS_SELECTOR, ".item-description")
    ITEM_PRICES = (By.CSS_SELECTOR, ".item-price")
    ITEM_QUANTITIES = (By.CSS_SELECTOR, ".quantity-input")
    QUANTITY_MINUS_BUTTONS = (By.CSS_SELECTOR, ".quantity-minus")
    QUANTITY_PLUS_BUTTONS = (By.CSS_SELECTOR, ".quantity-plus")
    ITEM_SUBTOTALS = (By.CSS_SELECTOR, ".item-subtotal")
    REMOVE_BUTTONS = (By.CSS_SELECTOR, ".remove-item")
    MOVE_TO_FAVORITES_BUTTONS = (By.CSS_SELECTOR, ".move-to-favorites")
    
    # 批量操作
    SELECT_ALL_CHECKBOX = (By.ID, "selectAll")
    BULK_REMOVE_BUTTON = (By.ID, "bulkRemove")
    BULK_MOVE_TO_FAVORITES_BUTTON = (By.ID, "bulkMoveToFavorites")
    
    # 购物车摘要
    CART_SUMMARY = (By.CSS_SELECTOR, ".cart-summary")
    SELECTED_ITEMS_COUNT = (By.CSS_SELECTOR, ".selected-items-count")
    SUBTOTAL_AMOUNT = (By.CSS_SELECTOR, ".subtotal-amount")
    SHIPPING_FEE = (By.CSS_SELECTOR, ".shipping-fee")
    DISCOUNT_AMOUNT = (By.CSS_SELECTOR, ".discount-amount")
    TOTAL_AMOUNT = (By.CSS_SELECTOR, ".total-amount")
    
    # 优惠券
    COUPON_INPUT = (By.ID, "couponCode")
    APPLY_COUPON_BUTTON = (By.ID, "applyCoupon")
    COUPON_MESSAGE = (By.CSS_SELECTOR, ".coupon-message")
    APPLIED_COUPONS = (By.CSS_SELECTOR, ".applied-coupon")
    REMOVE_COUPON_BUTTONS = (By.CSS_SELECTOR, ".remove-coupon")
    
    # 操作按钮
    CONTINUE_SHOPPING_BUTTON = (By.CSS_SELECTOR, ".continue-shopping")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, ".checkout-btn")
    CLEAR_CART_BUTTON = (By.CSS_SELECTOR, ".clear-cart")
    
    # 空购物车状态
    EMPTY_CART_MESSAGE = (By.CSS_SELECTOR, ".empty-cart")
    EMPTY_CART_IMAGE = (By.CSS_SELECTOR, ".empty-cart img")
    GO_SHOPPING_BUTTON = (By.CSS_SELECTOR, ".go-shopping")
    
    # 推荐商品
    RECOMMENDED_PRODUCTS = (By.CSS_SELECTOR, ".recommended-products")
    RECOMMENDED_PRODUCT_CARDS = (By.CSS_SELECTOR, ".recommended-product-card")
    
    # 提示消息
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    WARNING_MESSAGE = (By.CSS_SELECTOR, ".alert-warning")
    
    # 加载状态
    LOADING_SPINNER = (By.CSS_SELECTOR, ".loading-spinner")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open(self):
        """打开购物车页面"""
        super().open(self.PAGE_URL)
        return self
    
    def get_cart_items_count(self):
        """获取购物车商品数量"""
        items = self.find_elements(self.CART_ITEMS)
        return len(items)
    
    def get_item_info(self, index):
        """获取指定商品信息"""
        titles = self.find_elements(self.ITEM_TITLES)
        descriptions = self.find_elements(self.ITEM_DESCRIPTIONS)
        prices = self.find_elements(self.ITEM_PRICES)
        quantities = self.find_elements(self.ITEM_QUANTITIES)
        subtotals = self.find_elements(self.ITEM_SUBTOTALS)
        
        if 0 <= index < len(titles):
            return {
                "title": titles[index].text,
                "description": descriptions[index].text if index < len(descriptions) else "",
                "price": prices[index].text if index < len(prices) else "",
                "quantity": int(quantities[index].get_attribute("value")) if index < len(quantities) else 0,
                "subtotal": subtotals[index].text if index < len(subtotals) else ""
            }
        return None
    
    def get_all_items_info(self):
        """获取所有商品信息"""
        items_count = self.get_cart_items_count()
        items = []
        
        for i in range(items_count):
            item_info = self.get_item_info(i)
            if item_info:
                items.append(item_info)
        
        return items
    
    def select_item(self, index):
        """选择商品复选框"""
        checkboxes = self.find_elements(self.ITEM_CHECKBOXES)
        if 0 <= index < len(checkboxes):
            self.scroll_to_element(checkboxes[index])
            checkboxes[index].click()
        return self
    
    def select_all_items(self):
        """选择所有商品"""
        self.click(self.SELECT_ALL_CHECKBOX)
        return self
    
    def is_item_selected(self, index):
        """检查商品是否被选中"""
        checkboxes = self.find_elements(self.ITEM_CHECKBOXES)
        if 0 <= index < len(checkboxes):
            return checkboxes[index].is_selected()
        return False
    
    def get_selected_items_count_display(self):
        """获取显示的选中商品数量"""
        if self.is_element_visible(self.SELECTED_ITEMS_COUNT, timeout=3):
            return self.get_text(self.SELECTED_ITEMS_COUNT)
        return None
    
    def update_item_quantity(self, index, quantity):
        """更新商品数量"""
        quantity_inputs = self.find_elements(self.ITEM_QUANTITIES)
        if 0 <= index < len(quantity_inputs):
            self.scroll_to_element(quantity_inputs[index])
            quantity_inputs[index].clear()
            quantity_inputs[index].send_keys(str(quantity))
            # 触发change事件
            quantity_inputs[index].send_keys("\t")
        return self
    
    def increase_item_quantity(self, index):
        """增加商品数量"""
        plus_buttons = self.find_elements(self.QUANTITY_PLUS_BUTTONS)
        if 0 <= index < len(plus_buttons):
            self.scroll_to_element(plus_buttons[index])
            plus_buttons[index].click()
        return self
    
    def decrease_item_quantity(self, index):
        """减少商品数量"""
        minus_buttons = self.find_elements(self.QUANTITY_MINUS_BUTTONS)
        if 0 <= index < len(minus_buttons):
            self.scroll_to_element(minus_buttons[index])
            minus_buttons[index].click()
        return self
    
    def remove_item(self, index):
        """移除商品"""
        remove_buttons = self.find_elements(self.REMOVE_BUTTONS)
        if 0 <= index < len(remove_buttons):
            self.scroll_to_element(remove_buttons[index])
            remove_buttons[index].click()
            # 等待确认对话框并确认
            self.handle_alert(accept=True)
        return self
    
    def move_item_to_favorites(self, index):
        """移动商品到收藏夹"""
        move_buttons = self.find_elements(self.MOVE_TO_FAVORITES_BUTTONS)
        if 0 <= index < len(move_buttons):
            self.scroll_to_element(move_buttons[index])
            move_buttons[index].click()
        return self
    
    def bulk_remove_selected(self):
        """批量删除选中商品"""
        self.click(self.BULK_REMOVE_BUTTON)
        # 等待确认对话框并确认
        self.handle_alert(accept=True)
        return self
    
    def bulk_move_to_favorites(self):
        """批量移动选中商品到收藏夹"""
        self.click(self.BULK_MOVE_TO_FAVORITES_BUTTON)
        return self
    
    def get_subtotal_amount(self):
        """获取小计金额"""
        return self.get_text(self.SUBTOTAL_AMOUNT)
    
    def get_shipping_fee(self):
        """获取运费"""
        return self.get_text(self.SHIPPING_FEE)
    
    def get_discount_amount(self):
        """获取优惠金额"""
        return self.get_text(self.DISCOUNT_AMOUNT)
    
    def get_total_amount(self):
        """获取总金额"""
        return self.get_text(self.TOTAL_AMOUNT)
    
    def get_cart_summary(self):
        """获取购物车摘要信息"""
        return {
            "selected_items_count": self.get_selected_items_count_display(),
            "subtotal": self.get_subtotal_amount(),
            "shipping_fee": self.get_shipping_fee(),
            "discount": self.get_discount_amount(),
            "total": self.get_total_amount()
        }
    
    def apply_coupon(self, coupon_code):
        """应用优惠券"""
        self.send_keys(self.COUPON_INPUT, coupon_code)
        self.click(self.APPLY_COUPON_BUTTON)
        return self
    
    def get_coupon_message(self):
        """获取优惠券消息"""
        if self.is_element_visible(self.COUPON_MESSAGE, timeout=3):
            return self.get_text(self.COUPON_MESSAGE)
        return None
    
    def get_applied_coupons(self):
        """获取已应用的优惠券列表"""
        coupons = []
        coupon_elements = self.find_elements(self.APPLIED_COUPONS)
        
        for element in coupon_elements:
            coupons.append(element.text)
        
        return coupons
    
    def remove_coupon(self, index):
        """移除优惠券"""
        remove_buttons = self.find_elements(self.REMOVE_COUPON_BUTTONS)
        if 0 <= index < len(remove_buttons):
            remove_buttons[index].click()
        return self
    
    def continue_shopping(self):
        """继续购物"""
        self.click(self.CONTINUE_SHOPPING_BUTTON)
        return self
    
    def proceed_to_checkout(self):
        """进入结算页面"""
        self.click(self.CHECKOUT_BUTTON)
        return self
    
    def clear_cart(self):
        """清空购物车"""
        self.click(self.CLEAR_CART_BUTTON)
        # 等待确认对话框并确认
        self.handle_alert(accept=True)
        return self
    
    def is_cart_empty(self):
        """检查购物车是否为空"""
        return self.is_element_visible(self.EMPTY_CART_MESSAGE, timeout=3)
    
    def get_empty_cart_message(self):
        """获取空购物车消息"""
        if self.is_cart_empty():
            return self.get_text(self.EMPTY_CART_MESSAGE)
        return None
    
    def go_shopping_from_empty_cart(self):
        """从空购物车页面去购物"""
        if self.is_element_visible(self.GO_SHOPPING_BUTTON, timeout=3):
            self.click(self.GO_SHOPPING_BUTTON)
        return self
    
    def get_recommended_products_count(self):
        """获取推荐商品数量"""
        products = self.find_elements(self.RECOMMENDED_PRODUCT_CARDS)
        return len(products)
    
    def click_recommended_product(self, index):
        """点击推荐商品"""
        products = self.find_elements(self.RECOMMENDED_PRODUCT_CARDS)
        if 0 <= index < len(products):
            self.scroll_to_element(products[index])
            products[index].click()
        return self
    
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
    
    def get_warning_message(self):
        """获取警告消息"""
        if self.is_element_visible(self.WARNING_MESSAGE, timeout=3):
            return self.get_text(self.WARNING_MESSAGE)
        return None
    
    def wait_for_cart_update(self, timeout=None):
        """等待购物车更新完成"""
        # 等待加载动画消失
        if self.is_element_visible(self.LOADING_SPINNER, timeout=3):
            self.wait_for_element_to_disappear(self.LOADING_SPINNER, timeout)
        
        # 等待购物车摘要更新
        self.wait_for_element_visible(self.CART_SUMMARY, timeout)
        return self
    
    def get_selected_items_count(self):
        """获取实际选中的商品数量"""
        checkboxes = self.find_elements(self.ITEM_CHECKBOXES)
        selected_count = 0
        
        for checkbox in checkboxes:
            if checkbox.is_selected():
                selected_count += 1
        
        return selected_count
    
    def is_checkout_button_enabled(self):
        """检查结算按钮是否可用"""
        if self.is_element_visible(self.CHECKOUT_BUTTON, timeout=3):
            button = self.find_element(self.CHECKOUT_BUTTON)
            return button.is_enabled() and "disabled" not in button.get_attribute("class")
        return False
    
    def get_item_by_title(self, title):
        """根据商品标题获取商品索引"""
        titles = self.find_elements(self.ITEM_TITLES)
        
        for i, title_element in enumerate(titles):
            if title in title_element.text:
                return i
        
        return -1
    
    def verify_item_in_cart(self, title):
        """验证商品是否在购物车中"""
        return self.get_item_by_title(title) >= 0
    
    def get_cart_page_info(self):
        """获取购物车页面完整信息"""
        return {
            "is_empty": self.is_cart_empty(),
            "items_count": self.get_cart_items_count(),
            "selected_items_count": self.get_selected_items_count(),
            "cart_summary": self.get_cart_summary(),
            "applied_coupons": self.get_applied_coupons(),
            "recommended_products_count": self.get_recommended_products_count(),
            "checkout_button_enabled": self.is_checkout_button_enabled(),
            "success_message": self.get_success_message(),
            "error_message": self.get_error_message(),
            "warning_message": self.get_warning_message()
        }
    
    def perform_cart_operations_test(self):
        """执行购物车操作测试"""
        operations_log = []
        
        # 记录初始状态
        initial_count = self.get_cart_items_count()
        operations_log.append(f"初始商品数量: {initial_count}")
        
        if initial_count > 0:
            # 选择第一个商品
            self.select_item(0)
            operations_log.append("选择第一个商品")
            
            # 增加数量
            self.increase_item_quantity(0)
            operations_log.append("增加第一个商品数量")
            
            # 应用优惠券
            self.apply_coupon("TEST10")
            coupon_msg = self.get_coupon_message()
            operations_log.append(f"应用优惠券结果: {coupon_msg}")
            
            # 获取摘要信息
            summary = self.get_cart_summary()
            operations_log.append(f"购物车摘要: {summary}")
        
        return operations_log