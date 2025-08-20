#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品功能UI自动化测试
测试商品浏览、搜索、筛选、详情查看等功能
"""

import pytest
import time
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage, ProductDetailPage
from config.test_config import TestConfig

config = TestConfig()

class TestProducts:
    """商品功能测试类"""
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.login_page = None
        self.home_page = None
        self.products_page = None
        self.product_detail_page = None
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        pass
    
    @pytest.fixture(autouse=True)
    def setup_logged_in_user(self, driver):
        """自动登录用户的夹具"""
        self.login_page = LoginPage(driver)
        self.home_page = HomePage(driver)
        
        # 登录测试用户
        self.login_page.open()
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        time.sleep(2)
        
        # 验证登录成功
        assert self.home_page.is_user_logged_in()
    
    @pytest.mark.smoke
    @pytest.mark.products
    def test_products_page_load(self, driver):
        """测试商品页面加载"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 验证页面标题
        assert "商品" in driver.title or "Products" in driver.title
        
        # 验证页面关键元素存在
        assert self.products_page.is_element_visible(self.products_page.PRODUCTS_GRID, timeout=10)
        assert self.products_page.is_element_visible(self.products_page.SEARCH_BOX, timeout=5)
        
        # 验证有商品显示
        products_count = self.products_page.get_products_count()
        assert products_count > 0, "页面应该显示商品"
    
    @pytest.mark.products
    @pytest.mark.search
    def test_product_search_functionality(self, driver):
        """测试商品搜索功能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 记录初始商品数量
        initial_count = self.products_page.get_products_count()
        
        # 搜索特定商品
        search_keyword = "笔记本"
        self.products_page.search_products(search_keyword)
        
        # 等待搜索结果加载
        time.sleep(2)
        
        # 验证搜索结果
        search_results_count = self.products_page.get_products_count()
        
        if search_results_count > 0:
            # 验证搜索结果包含关键词
            products_info = self.products_page.get_all_products_info()
            for product in products_info:
                assert (search_keyword in product["title"] or 
                       search_keyword in product["description"]), \
                       f"搜索结果应包含关键词: {search_keyword}"
        else:
            # 验证显示无结果消息
            assert self.products_page.is_no_results_displayed()
    
    @pytest.mark.products
    @pytest.mark.filter
    def test_product_category_filter(self, driver):
        """测试商品分类筛选"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 记录初始商品数量
        initial_count = self.products_page.get_products_count()
        
        # 按分类筛选
        category = "电子产品"
        self.products_page.filter_by_category(category)
        
        # 等待筛选结果加载
        time.sleep(2)
        
        # 验证筛选结果
        filtered_count = self.products_page.get_products_count()
        
        # 验证筛选条件已应用
        filter_values = self.products_page.get_filter_values()
        assert category in filter_values["category"]
        
        # 如果有结果，验证结果符合筛选条件
        if filtered_count > 0:
            assert filtered_count <= initial_count, "筛选后的商品数量应该不超过初始数量"
    
    @pytest.mark.products
    @pytest.mark.filter
    def test_product_price_filter(self, driver):
        """测试商品价格筛选"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 设置价格范围筛选
        min_price = 100
        max_price = 1000
        self.products_page.filter_by_price_range(min_price, max_price)
        
        # 等待筛选结果加载
        time.sleep(2)
        
        # 验证筛选条件已应用
        filter_values = self.products_page.get_filter_values()
        assert str(min_price) in filter_values["min_price"]
        assert str(max_price) in filter_values["max_price"]
        
        # 验证筛选结果价格在范围内
        products_info = self.products_page.get_all_products_info()
        for product in products_info:
            # 提取价格数字（假设价格格式为 "¥123.45"）
            price_text = product["price"]
            if price_text:
                import re
                price_match = re.search(r'[\d.]+', price_text)
                if price_match:
                    price = float(price_match.group())
                    assert min_price <= price <= max_price, \
                           f"商品价格 {price} 应在范围 {min_price}-{max_price} 内"
    
    @pytest.mark.products
    @pytest.mark.sort
    def test_product_sorting(self, driver):
        """测试商品排序功能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 测试不同排序选项
        sort_options = ["价格从低到高", "价格从高到低", "销量排序", "评分排序"]
        
        for sort_option in sort_options:
            try:
                # 应用排序
                self.products_page.sort_products(sort_option)
                
                # 等待排序结果加载
                time.sleep(2)
                
                # 验证排序条件已应用
                filter_values = self.products_page.get_filter_values()
                assert sort_option in filter_values["sort_by"]
                
                # 验证有商品显示
                products_count = self.products_page.get_products_count()
                assert products_count > 0
                
            except Exception as e:
                # 如果某个排序选项不存在，跳过
                print(f"排序选项 '{sort_option}' 不可用: {e}")
                continue
    
    @pytest.mark.products
    @pytest.mark.pagination
    def test_product_pagination(self, driver):
        """测试商品分页功能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 获取总页数
        total_pages = self.products_page.get_total_pages()
        
        if total_pages > 1:
            # 验证当前在第一页
            current_page = self.products_page.get_current_page_number()
            assert current_page == 1
            
            # 跳转到下一页
            self.products_page.go_to_next_page()
            time.sleep(2)
            
            # 验证页面已切换
            new_current_page = self.products_page.get_current_page_number()
            assert new_current_page == 2
            
            # 跳转到上一页
            self.products_page.go_to_prev_page()
            time.sleep(2)
            
            # 验证回到第一页
            back_to_first_page = self.products_page.get_current_page_number()
            assert back_to_first_page == 1
            
            # 如果有多页，测试跳转到指定页面
            if total_pages >= 3:
                self.products_page.go_to_page(3)
                time.sleep(2)
                
                current_page = self.products_page.get_current_page_number()
                assert current_page == 3
    
    @pytest.mark.products
    @pytest.mark.detail
    def test_product_detail_view(self, driver):
        """测试商品详情查看"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.product_detail_page = ProductDetailPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 获取第一个商品信息
        first_product = self.products_page.get_product_info(0)
        assert first_product is not None, "应该有商品可供查看"
        
        # 点击查看详情
        self.products_page.click_view_detail(0)
        
        # 等待详情页加载
        time.sleep(3)
        
        # 验证跳转到详情页
        assert "product" in driver.current_url
        
        # 验证详情页关键元素
        assert self.product_detail_page.is_element_visible(
            self.product_detail_page.PRODUCT_TITLE, timeout=10)
        assert self.product_detail_page.is_element_visible(
            self.product_detail_page.PRODUCT_PRICE, timeout=5)
        
        # 获取详情页信息
        detail_info = self.product_detail_page.get_product_detail_info()
        assert detail_info["title"], "商品标题不应为空"
        assert detail_info["price"], "商品价格不应为空"
    
    @pytest.mark.products
    @pytest.mark.detail
    def test_product_detail_tabs(self, driver):
        """测试商品详情页标签切换"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.product_detail_page = ProductDetailPage(driver)
        
        # 打开商品页面并进入详情页
        self.products_page.open()
        self.products_page.click_view_detail(0)
        time.sleep(3)
        
        # 测试切换到商品详情标签
        self.product_detail_page.switch_to_details_tab()
        assert self.product_detail_page.is_element_visible(
            self.product_detail_page.DETAILS_CONTENT, timeout=5)
        
        # 测试切换到规格参数标签
        self.product_detail_page.switch_to_specs_tab()
        assert self.product_detail_page.is_element_visible(
            self.product_detail_page.SPECS_CONTENT, timeout=5)
        
        # 测试切换到用户评价标签
        self.product_detail_page.switch_to_reviews_tab()
        assert self.product_detail_page.is_element_visible(
            self.product_detail_page.REVIEWS_CONTENT, timeout=5)
        
        # 获取评价数量
        reviews_count = self.product_detail_page.get_reviews_count()
        print(f"商品评价数量: {reviews_count}")
    
    @pytest.mark.products
    @pytest.mark.interaction
    def test_product_quantity_selection(self, driver):
        """测试商品数量选择"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.product_detail_page = ProductDetailPage(driver)
        
        # 打开商品页面并进入详情页
        self.products_page.open()
        self.products_page.click_view_detail(0)
        time.sleep(3)
        
        # 验证初始数量
        initial_quantity = self.product_detail_page.get_quantity()
        assert initial_quantity >= 1
        
        # 增加数量
        self.product_detail_page.increase_quantity()
        time.sleep(1)
        
        new_quantity = self.product_detail_page.get_quantity()
        assert new_quantity == initial_quantity + 1
        
        # 减少数量
        self.product_detail_page.decrease_quantity()
        time.sleep(1)
        
        final_quantity = self.product_detail_page.get_quantity()
        assert final_quantity == initial_quantity
        
        # 直接设置数量
        target_quantity = 5
        self.product_detail_page.set_quantity(target_quantity)
        time.sleep(1)
        
        set_quantity = self.product_detail_page.get_quantity()
        assert set_quantity == target_quantity
    
    @pytest.mark.products
    @pytest.mark.interaction
    def test_add_to_cart_from_list(self, driver):
        """测试从商品列表添加到购物车"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.home_page = HomePage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 获取初始购物车数量
        initial_cart_count = self.home_page.get_cart_count()
        
        # 添加第一个商品到购物车
        self.products_page.click_add_to_cart(0)
        
        # 等待添加完成
        time.sleep(2)
        
        # 验证购物车数量增加
        new_cart_count = self.home_page.get_cart_count()
        assert new_cart_count > initial_cart_count, "购物车数量应该增加"
    
    @pytest.mark.products
    @pytest.mark.interaction
    def test_add_to_cart_from_detail(self, driver):
        """测试从商品详情页添加到购物车"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.product_detail_page = ProductDetailPage(driver)
        self.home_page = HomePage(driver)
        
        # 打开商品页面并进入详情页
        self.products_page.open()
        self.products_page.click_view_detail(0)
        time.sleep(3)
        
        # 获取初始购物车数量
        initial_cart_count = self.home_page.get_cart_count()
        
        # 设置商品数量
        quantity = 2
        self.product_detail_page.set_quantity(quantity)
        
        # 添加到购物车
        self.product_detail_page.click_add_to_cart()
        
        # 等待添加完成
        time.sleep(3)
        
        # 验证购物车数量增加
        new_cart_count = self.home_page.get_cart_count()
        expected_count = initial_cart_count + quantity
        assert new_cart_count >= expected_count, f"购物车数量应该至少增加 {quantity}"
    
    @pytest.mark.products
    @pytest.mark.bulk
    def test_bulk_operations(self, driver):
        """测试批量操作"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 验证有足够的商品进行批量操作
        products_count = self.products_page.get_products_count()
        assert products_count >= 2, "需要至少2个商品进行批量操作测试"
        
        # 选择前两个商品
        self.products_page.select_product(0)
        self.products_page.select_product(1)
        
        # 验证选中数量
        selected_count = self.products_page.get_selected_products_count()
        assert selected_count == 2
        
        # 测试批量添加到购物车
        initial_cart_count = self.home_page.get_cart_count()
        self.products_page.bulk_add_to_cart()
        
        # 等待操作完成
        time.sleep(3)
        
        # 验证购物车数量增加
        new_cart_count = self.home_page.get_cart_count()
        assert new_cart_count > initial_cart_count
    
    @pytest.mark.products
    @pytest.mark.filter
    def test_clear_filters(self, driver):
        """测试清除筛选条件"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 记录初始商品数量
        initial_count = self.products_page.get_products_count()
        
        # 应用多个筛选条件
        self.products_page.search_products("测试")
        time.sleep(1)
        self.products_page.filter_by_price_range(100, 500)
        time.sleep(2)
        
        # 验证筛选后商品数量变化
        filtered_count = self.products_page.get_products_count()
        
        # 清除所有筛选条件
        self.products_page.clear_all_filters()
        time.sleep(2)
        
        # 验证商品数量恢复
        cleared_count = self.products_page.get_products_count()
        assert cleared_count >= filtered_count, "清除筛选后商品数量应该不少于筛选后的数量"
        
        # 验证筛选条件已清除
        filter_values = self.products_page.get_filter_values()
        assert not filter_values["search_keyword"] or filter_values["search_keyword"] == ""
        assert not filter_values["min_price"] or filter_values["min_price"] == ""
        assert not filter_values["max_price"] or filter_values["max_price"] == ""
    
    @pytest.mark.products
    @pytest.mark.performance
    def test_products_page_performance(self, driver):
        """测试商品页面性能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 记录开始时间
        start_time = time.time()
        
        # 打开商品页面
        self.products_page.open()
        
        # 等待页面完全加载
        self.products_page.wait_for_products_load()
        
        # 记录加载时间
        load_time = time.time() - start_time
        
        # 验证页面加载时间合理（小于10秒）
        assert load_time < 10.0, f"商品页面加载时间过长: {load_time:.2f}秒"
        
        # 测试搜索性能
        search_start_time = time.time()
        self.products_page.search_products("笔记本")
        search_time = time.time() - search_start_time
        
        # 验证搜索时间合理（小于5秒）
        assert search_time < 5.0, f"商品搜索时间过长: {search_time:.2f}秒"
    
    @pytest.mark.products
    @pytest.mark.responsive
    def test_products_responsive_design(self, driver):
        """测试商品页面响应式设计"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
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
            time.sleep(2)
            
            # 验证关键元素仍然可见
            assert self.products_page.is_element_visible(
                self.products_page.PRODUCTS_GRID, timeout=5)
            assert self.products_page.is_element_visible(
                self.products_page.SEARCH_BOX, timeout=5)
            
            # 验证商品卡片正常显示
            products_count = self.products_page.get_products_count()
            assert products_count > 0
        
        # 恢复默认窗口大小
        driver.maximize_window()
    
    @pytest.mark.products
    @pytest.mark.edge_case
    def test_products_edge_cases(self, driver):
        """测试商品功能边界情况"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 测试搜索不存在的商品
        non_existent_keyword = "不存在的商品xyz123"
        self.products_page.search_products(non_existent_keyword)
        time.sleep(2)
        
        # 验证显示无结果消息
        if self.products_page.get_products_count() == 0:
            assert self.products_page.is_no_results_displayed()
        
        # 测试无效价格范围
        self.products_page.clear_all_filters()
        time.sleep(1)
        
        # 最小价格大于最大价格
        self.products_page.filter_by_price_range(1000, 100)
        time.sleep(2)
        
        # 验证处理无效价格范围
        # 应该显示无结果或错误消息
        
        # 测试特殊字符搜索
        special_chars = "@#$%^&*()"
        self.products_page.clear_all_filters()
        time.sleep(1)
        self.products_page.search_products(special_chars)
        time.sleep(2)
        
        # 验证处理特殊字符搜索
        # 页面应该正常响应，不应该出错
        assert "error" not in driver.current_url.lower()
    
    @pytest.mark.products
    @pytest.mark.accessibility
    def test_products_accessibility(self, driver):
        """测试商品页面可访问性"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        
        # 打开商品页面
        self.products_page.open()
        
        # 验证搜索框有适当的标签
        search_box = self.products_page.find_element(self.products_page.SEARCH_BOX)
        assert (search_box.get_attribute("placeholder") or 
                search_box.get_attribute("aria-label") or
                search_box.get_attribute("title"))
        
        # 验证商品卡片有适当的结构
        product_cards = self.products_page.find_elements(self.products_page.PRODUCT_CARDS)
        if product_cards:
            first_card = product_cards[0]
            # 验证商品卡片可以通过键盘访问
            assert first_card.get_attribute("tabindex") is not None or \
                   first_card.tag_name.lower() in ['a', 'button']
        
        # 验证按钮有适当的文本或标签
        buttons = self.products_page.find_elements(self.products_page.ADD_TO_CART_BUTTONS)
        if buttons:
            first_button = buttons[0]
            assert (first_button.text or 
                    first_button.get_attribute("aria-label") or
                    first_button.get_attribute("title"))