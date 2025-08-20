#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品页面对象模型
封装商品列表页面和商品详情页面的元素和操作
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage
from config.test_config import TestConfig

config = TestConfig()

class ProductsPage(BasePage):
    """商品列表页面对象"""
    
    # 页面URL
    PAGE_URL = f"{config.BASE_URL}/products"
    
    # 搜索和筛选区域
    SEARCH_BOX = (By.ID, "searchBox")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".search-btn")
    CATEGORY_SELECT = (By.ID, "categoryFilter")
    MIN_PRICE_INPUT = (By.ID, "minPrice")
    MAX_PRICE_INPUT = (By.ID, "maxPrice")
    PRICE_FILTER_BUTTON = (By.ID, "applyPriceFilter")
    SORT_SELECT = (By.ID, "sortBy")
    CLEAR_FILTERS_BUTTON = (By.ID, "clearFilters")
    
    # 商品网格
    PRODUCTS_GRID = (By.CSS_SELECTOR, ".products-grid")
    PRODUCT_CARDS = (By.CSS_SELECTOR, ".product-card")
    PRODUCT_IMAGES = (By.CSS_SELECTOR, ".product-card img")
    PRODUCT_TITLES = (By.CSS_SELECTOR, ".product-card h5")
    PRODUCT_DESCRIPTIONS = (By.CSS_SELECTOR, ".product-card .text-muted")
    PRODUCT_PRICES = (By.CSS_SELECTOR, ".product-card .price")
    PRODUCT_STOCKS = (By.CSS_SELECTOR, ".product-card .stock")
    VIEW_DETAIL_BUTTONS = (By.CSS_SELECTOR, ".btn-outline-primary")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, ".add-to-cart")
    
    # 批量操作
    SELECT_ALL_CHECKBOX = (By.ID, "selectAll")
    PRODUCT_CHECKBOXES = (By.CSS_SELECTOR, ".product-checkbox")
    BULK_ADD_TO_CART_BUTTON = (By.ID, "bulkAddToCart")
    COMPARE_BUTTON = (By.ID, "compareProducts")
    
    # 分页
    PAGINATION = (By.CSS_SELECTOR, ".pagination")
    PAGINATION_PREV = (By.CSS_SELECTOR, ".page-link[aria-label='Previous']")
    PAGINATION_NEXT = (By.CSS_SELECTOR, ".page-link[aria-label='Next']")
    PAGINATION_PAGES = (By.CSS_SELECTOR, ".page-link:not([aria-label])")
    
    # 结果信息
    RESULTS_COUNT = (By.CSS_SELECTOR, ".results-count")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, ".no-results")
    
    # 加载状态
    LOADING_SPINNER = (By.CSS_SELECTOR, ".loading-spinner")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open(self):
        """打开商品列表页面"""
        super().open(self.PAGE_URL)
        return self
    
    def search_products(self, keyword):
        """搜索商品"""
        self.send_keys(self.SEARCH_BOX, keyword)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_products_load()
        return self
    
    def filter_by_category(self, category):
        """按分类筛选"""
        select_element = self.find_element(self.CATEGORY_SELECT)
        select = Select(select_element)
        select.select_by_visible_text(category)
        self.wait_for_products_load()
        return self
    
    def filter_by_price_range(self, min_price, max_price):
        """按价格范围筛选"""
        if min_price is not None:
            self.send_keys(self.MIN_PRICE_INPUT, str(min_price))
        if max_price is not None:
            self.send_keys(self.MAX_PRICE_INPUT, str(max_price))
        self.click(self.PRICE_FILTER_BUTTON)
        self.wait_for_products_load()
        return self
    
    def sort_products(self, sort_option):
        """排序商品"""
        select_element = self.find_element(self.SORT_SELECT)
        select = Select(select_element)
        select.select_by_visible_text(sort_option)
        self.wait_for_products_load()
        return self
    
    def clear_all_filters(self):
        """清除所有筛选条件"""
        self.click(self.CLEAR_FILTERS_BUTTON)
        self.wait_for_products_load()
        return self
    
    def get_products_count(self):
        """获取商品数量"""
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
        """获取所有商品信息"""
        products_count = self.get_products_count()
        products = []
        
        for i in range(products_count):
            product_info = self.get_product_info(i)
            if product_info:
                products.append(product_info)
        
        return products
    
    def click_view_detail(self, index):
        """点击查看详情"""
        buttons = self.find_elements(self.VIEW_DETAIL_BUTTONS)
        if 0 <= index < len(buttons):
            self.scroll_to_element(buttons[index])
            buttons[index].click()
        return self
    
    def click_add_to_cart(self, index):
        """点击添加到购物车"""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTONS)
        if 0 <= index < len(buttons):
            self.scroll_to_element(buttons[index])
            buttons[index].click()
        return self
    
    def select_product(self, index):
        """选择商品复选框"""
        checkboxes = self.find_elements(self.PRODUCT_CHECKBOXES)
        if 0 <= index < len(checkboxes):
            self.scroll_to_element(checkboxes[index])
            checkboxes[index].click()
        return self
    
    def select_all_products(self):
        """选择所有商品"""
        self.click(self.SELECT_ALL_CHECKBOX)
        return self
    
    def bulk_add_to_cart(self):
        """批量添加到购物车"""
        self.click(self.BULK_ADD_TO_CART_BUTTON)
        return self
    
    def compare_products(self):
        """比较商品"""
        self.click(self.COMPARE_BUTTON)
        return self
    
    def go_to_page(self, page_number):
        """跳转到指定页面"""
        page_links = self.find_elements(self.PAGINATION_PAGES)
        for link in page_links:
            if link.text == str(page_number):
                link.click()
                self.wait_for_products_load()
                break
        return self
    
    def go_to_next_page(self):
        """跳转到下一页"""
        if self.is_element_clickable(self.PAGINATION_NEXT, timeout=3):
            self.click(self.PAGINATION_NEXT)
            self.wait_for_products_load()
        return self
    
    def go_to_prev_page(self):
        """跳转到上一页"""
        if self.is_element_clickable(self.PAGINATION_PREV, timeout=3):
            self.click(self.PAGINATION_PREV)
            self.wait_for_products_load()
        return self
    
    def get_current_page_number(self):
        """获取当前页码"""
        page_links = self.find_elements(self.PAGINATION_PAGES)
        for link in page_links:
            if "active" in link.get_attribute("class"):
                return int(link.text)
        return 1
    
    def get_total_pages(self):
        """获取总页数"""
        page_links = self.find_elements(self.PAGINATION_PAGES)
        if page_links:
            return int(page_links[-1].text)
        return 1
    
    def get_results_count_text(self):
        """获取结果数量文本"""
        if self.is_element_visible(self.RESULTS_COUNT, timeout=3):
            return self.get_text(self.RESULTS_COUNT)
        return None
    
    def is_no_results_displayed(self):
        """检查是否显示无结果消息"""
        return self.is_element_visible(self.NO_RESULTS_MESSAGE, timeout=3)
    
    def wait_for_products_load(self, timeout=None):
        """等待商品加载完成"""
        # 等待加载动画消失
        if self.is_element_visible(self.LOADING_SPINNER, timeout=3):
            self.wait_for_element_to_disappear(self.LOADING_SPINNER, timeout)
        
        # 等待商品网格出现
        self.wait_for_element_visible(self.PRODUCTS_GRID, timeout)
        return self
    
    def get_selected_products_count(self):
        """获取选中的商品数量"""
        checkboxes = self.find_elements(self.PRODUCT_CHECKBOXES)
        selected_count = 0
        for checkbox in checkboxes:
            if checkbox.is_selected():
                selected_count += 1
        return selected_count
    
    def get_filter_values(self):
        """获取当前筛选条件"""
        category_select = Select(self.find_element(self.CATEGORY_SELECT))
        sort_select = Select(self.find_element(self.SORT_SELECT))
        
        return {
            "search_keyword": self.get_attribute(self.SEARCH_BOX, "value"),
            "category": category_select.first_selected_option.text,
            "min_price": self.get_attribute(self.MIN_PRICE_INPUT, "value"),
            "max_price": self.get_attribute(self.MAX_PRICE_INPUT, "value"),
            "sort_by": sort_select.first_selected_option.text
        }

class ProductDetailPage(BasePage):
    """商品详情页面对象"""
    
    # 面包屑导航
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")
    BREADCRUMB_LINKS = (By.CSS_SELECTOR, ".breadcrumb a")
    
    # 商品图片
    MAIN_IMAGE = (By.CSS_SELECTOR, ".main-image img")
    THUMBNAIL_IMAGES = (By.CSS_SELECTOR, ".thumbnail img")
    
    # 商品信息
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".product-title")
    PRODUCT_RATING = (By.CSS_SELECTOR, ".rating")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".price")
    PRODUCT_STOCK = (By.CSS_SELECTOR, ".stock")
    
    # 商品属性
    PRODUCT_ATTRIBUTES = (By.CSS_SELECTOR, ".product-attributes")
    ATTRIBUTE_ITEMS = (By.CSS_SELECTOR, ".attribute-item")
    
    # 规格选择
    SPEC_OPTIONS = (By.CSS_SELECTOR, ".spec-option")
    COLOR_OPTIONS = (By.CSS_SELECTOR, ".color-option")
    SIZE_OPTIONS = (By.CSS_SELECTOR, ".size-option")
    
    # 数量选择
    QUANTITY_INPUT = (By.CSS_SELECTOR, ".quantity-input")
    QUANTITY_MINUS = (By.CSS_SELECTOR, ".quantity-minus")
    QUANTITY_PLUS = (By.CSS_SELECTOR, ".quantity-plus")
    
    # 操作按钮
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, ".add-to-cart")
    BUY_NOW_BUTTON = (By.CSS_SELECTOR, ".buy-now")
    ADD_TO_FAVORITES_BUTTON = (By.CSS_SELECTOR, ".add-to-favorites")
    SHARE_BUTTON = (By.CSS_SELECTOR, ".share-btn")
    NOTIFY_BUTTON = (By.CSS_SELECTOR, ".notify-btn")
    
    # 标签页
    TAB_DETAILS = (By.CSS_SELECTOR, "[data-bs-target='#details']")
    TAB_SPECS = (By.CSS_SELECTOR, "[data-bs-target='#specs']")
    TAB_REVIEWS = (By.CSS_SELECTOR, "[data-bs-target='#reviews']")
    
    # 标签页内容
    DETAILS_CONTENT = (By.ID, "details")
    SPECS_CONTENT = (By.ID, "specs")
    REVIEWS_CONTENT = (By.ID, "reviews")
    
    # 评价相关
    REVIEW_ITEMS = (By.CSS_SELECTOR, ".review-item")
    REVIEW_RATINGS = (By.CSS_SELECTOR, ".review-rating")
    REVIEW_CONTENTS = (By.CSS_SELECTOR, ".review-content")
    REVIEW_AUTHORS = (By.CSS_SELECTOR, ".review-author")
    REVIEW_DATES = (By.CSS_SELECTOR, ".review-date")
    LIKE_BUTTONS = (By.CSS_SELECTOR, ".like-btn")
    REPLY_BUTTONS = (By.CSS_SELECTOR, ".reply-btn")
    
    # 相关商品
    RELATED_PRODUCTS = (By.CSS_SELECTOR, ".related-products")
    RELATED_PRODUCT_CARDS = (By.CSS_SELECTOR, ".related-product-card")
    
    # 服务保障
    SERVICE_GUARANTEES = (By.CSS_SELECTOR, ".service-guarantee")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open(self, product_id):
        """打开商品详情页面"""
        url = f"{config.BASE_URL}/product/{product_id}"
        super().open(url)
        return self
    
    def click_thumbnail(self, index):
        """点击缩略图"""
        thumbnails = self.find_elements(self.THUMBNAIL_IMAGES)
        if 0 <= index < len(thumbnails):
            thumbnails[index].click()
        return self
    
    def get_product_title(self):
        """获取商品标题"""
        return self.get_text(self.PRODUCT_TITLE)
    
    def get_product_price(self):
        """获取商品价格"""
        return self.get_text(self.PRODUCT_PRICE)
    
    def get_product_stock(self):
        """获取商品库存"""
        return self.get_text(self.PRODUCT_STOCK)
    
    def get_product_rating(self):
        """获取商品评分"""
        return self.get_text(self.PRODUCT_RATING)
    
    def select_spec_option(self, spec_type, option_value):
        """选择规格选项"""
        # 这里需要根据实际的HTML结构来实现
        spec_options = self.find_elements(self.SPEC_OPTIONS)
        for option in spec_options:
            if option_value in option.text:
                option.click()
                break
        return self
    
    def set_quantity(self, quantity):
        """设置商品数量"""
        self.send_keys(self.QUANTITY_INPUT, str(quantity))
        return self
    
    def increase_quantity(self):
        """增加商品数量"""
        self.click(self.QUANTITY_PLUS)
        return self
    
    def decrease_quantity(self):
        """减少商品数量"""
        self.click(self.QUANTITY_MINUS)
        return self
    
    def get_quantity(self):
        """获取当前数量"""
        return int(self.get_attribute(self.QUANTITY_INPUT, "value"))
    
    def click_add_to_cart(self):
        """点击添加到购物车"""
        self.click(self.ADD_TO_CART_BUTTON)
        return self
    
    def click_buy_now(self):
        """点击立即购买"""
        self.click(self.BUY_NOW_BUTTON)
        return self
    
    def click_add_to_favorites(self):
        """点击添加到收藏"""
        self.click(self.ADD_TO_FAVORITES_BUTTON)
        return self
    
    def click_share(self):
        """点击分享"""
        self.click(self.SHARE_BUTTON)
        return self
    
    def click_notify(self):
        """点击到货通知"""
        self.click(self.NOTIFY_BUTTON)
        return self
    
    def switch_to_details_tab(self):
        """切换到商品详情标签页"""
        self.click(self.TAB_DETAILS)
        self.wait_for_element_visible(self.DETAILS_CONTENT)
        return self
    
    def switch_to_specs_tab(self):
        """切换到规格参数标签页"""
        self.click(self.TAB_SPECS)
        self.wait_for_element_visible(self.SPECS_CONTENT)
        return self
    
    def switch_to_reviews_tab(self):
        """切换到用户评价标签页"""
        self.click(self.TAB_REVIEWS)
        self.wait_for_element_visible(self.REVIEWS_CONTENT)
        return self
    
    def get_reviews_count(self):
        """获取评价数量"""
        reviews = self.find_elements(self.REVIEW_ITEMS)
        return len(reviews)
    
    def get_review_info(self, index):
        """获取指定评价信息"""
        ratings = self.find_elements(self.REVIEW_RATINGS)
        contents = self.find_elements(self.REVIEW_CONTENTS)
        authors = self.find_elements(self.REVIEW_AUTHORS)
        dates = self.find_elements(self.REVIEW_DATES)
        
        if 0 <= index < len(contents):
            return {
                "rating": ratings[index].text if index < len(ratings) else "",
                "content": contents[index].text,
                "author": authors[index].text if index < len(authors) else "",
                "date": dates[index].text if index < len(dates) else ""
            }
        return None
    
    def like_review(self, index):
        """点赞评价"""
        like_buttons = self.find_elements(self.LIKE_BUTTONS)
        if 0 <= index < len(like_buttons):
            like_buttons[index].click()
        return self
    
    def reply_to_review(self, index):
        """回复评价"""
        reply_buttons = self.find_elements(self.REPLY_BUTTONS)
        if 0 <= index < len(reply_buttons):
            reply_buttons[index].click()
        return self
    
    def get_related_products_count(self):
        """获取相关商品数量"""
        products = self.find_elements(self.RELATED_PRODUCT_CARDS)
        return len(products)
    
    def click_related_product(self, index):
        """点击相关商品"""
        products = self.find_elements(self.RELATED_PRODUCT_CARDS)
        if 0 <= index < len(products):
            self.scroll_to_element(products[index])
            products[index].click()
        return self
    
    def get_breadcrumb_path(self):
        """获取面包屑导航路径"""
        links = self.find_elements(self.BREADCRUMB_LINKS)
        path = []
        for link in links:
            path.append(link.text)
        return path
    
    def click_breadcrumb_link(self, index):
        """点击面包屑导航链接"""
        links = self.find_elements(self.BREADCRUMB_LINKS)
        if 0 <= index < len(links):
            links[index].click()
        return self
    
    def get_product_attributes(self):
        """获取商品属性"""
        attributes = {}
        attribute_items = self.find_elements(self.ATTRIBUTE_ITEMS)
        
        for item in attribute_items:
            # 假设属性格式为 "属性名: 属性值"
            text = item.text
            if ":" in text:
                key, value = text.split(":", 1)
                attributes[key.strip()] = value.strip()
        
        return attributes
    
    def get_service_guarantees(self):
        """获取服务保障信息"""
        guarantees = []
        guarantee_elements = self.find_elements(self.SERVICE_GUARANTEES)
        
        for element in guarantee_elements:
            guarantees.append(element.text)
        
        return guarantees
    
    def get_product_detail_info(self):
        """获取商品详情页完整信息"""
        return {
            "title": self.get_product_title(),
            "price": self.get_product_price(),
            "stock": self.get_product_stock(),
            "rating": self.get_product_rating(),
            "quantity": self.get_quantity(),
            "attributes": self.get_product_attributes(),
            "breadcrumb_path": self.get_breadcrumb_path(),
            "reviews_count": self.get_reviews_count(),
            "related_products_count": self.get_related_products_count(),
            "service_guarantees": self.get_service_guarantees()
        }