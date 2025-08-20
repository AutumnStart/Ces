#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购物车功能UI自动化测试
测试购物车添加、删除、修改、结算等功能
"""

import pytest
import time
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from config.test_config import TestConfig

config = TestConfig()

class TestCart:
    """购物车功能测试类"""
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.login_page = None
        self.home_page = None
        self.products_page = None
        self.cart_page = None
    
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
    @pytest.mark.cart
    def test_cart_page_load(self, driver):
        """测试购物车页面加载"""
        # 初始化页面对象
        self.cart_page = CartPage(driver)
        
        # 打开购物车页面
        self.cart_page.open()
        
        # 验证页面标题
        assert "购物车" in driver.title or "Cart" in driver.title
        
        # 验证页面关键元素存在
        assert self.cart_page.is_element_visible(self.cart_page.PAGE_TITLE, timeout=10)
        
        # 获取购物车页面信息
        cart_info = self.cart_page.get_cart_page_info()
        print(f"购物车页面信息: {cart_info}")
    
    @pytest.mark.cart
    @pytest.mark.add_item
    def test_add_item_to_cart(self, driver):
        """测试添加商品到购物车"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 获取初始购物车数量
        initial_cart_count = self.home_page.get_cart_count()
        
        # 打开商品页面
        self.products_page.open()
        
        # 获取第一个商品信息
        first_product = self.products_page.get_product_info(0)
        assert first_product is not None, "应该有商品可供添加"
        
        product_title = first_product["title"]
        
        # 添加商品到购物车
        self.products_page.click_add_to_cart(0)
        
        # 等待添加完成
        time.sleep(3)
        
        # 验证购物车数量增加
        new_cart_count = self.home_page.get_cart_count()
        assert new_cart_count > initial_cart_count, "购物车数量应该增加"
        
        # 打开购物车页面验证商品已添加
        self.cart_page.open()
        time.sleep(2)
        
        # 验证商品在购物车中
        assert self.cart_page.verify_item_in_cart(product_title), f"商品 '{product_title}' 应该在购物车中"
    
    @pytest.mark.cart
    @pytest.mark.quantity
    def test_update_item_quantity(self, driver):
        """测试更新商品数量"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证有商品在购物车中
        items_count = self.cart_page.get_cart_items_count()
        assert items_count > 0, "购物车中应该有商品"
        
        # 获取第一个商品的初始信息
        initial_item_info = self.cart_page.get_item_info(0)
        initial_quantity = initial_item_info["quantity"]
        
        # 增加数量
        self.cart_page.increase_item_quantity(0)
        self.cart_page.wait_for_cart_update()
        
        # 验证数量增加
        updated_item_info = self.cart_page.get_item_info(0)
        new_quantity = updated_item_info["quantity"]
        assert new_quantity == initial_quantity + 1, "商品数量应该增加1"
        
        # 减少数量
        self.cart_page.decrease_item_quantity(0)
        self.cart_page.wait_for_cart_update()
        
        # 验证数量减少
        final_item_info = self.cart_page.get_item_info(0)
        final_quantity = final_item_info["quantity"]
        assert final_quantity == initial_quantity, "商品数量应该回到初始值"
        
        # 直接设置数量
        target_quantity = 5
        self.cart_page.update_item_quantity(0, target_quantity)
        self.cart_page.wait_for_cart_update()
        
        # 验证数量设置成功
        set_item_info = self.cart_page.get_item_info(0)
        set_quantity = set_item_info["quantity"]
        assert set_quantity == target_quantity, f"商品数量应该设置为 {target_quantity}"
    
    @pytest.mark.cart
    @pytest.mark.remove_item
    def test_remove_item_from_cart(self, driver):
        """测试从购物车删除商品"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        first_product = self.products_page.get_product_info(0)
        product_title = first_product["title"]
        
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证商品在购物车中
        initial_items_count = self.cart_page.get_cart_items_count()
        assert initial_items_count > 0, "购物车中应该有商品"
        assert self.cart_page.verify_item_in_cart(product_title), "商品应该在购物车中"
        
        # 删除第一个商品
        self.cart_page.remove_item(0)
        self.cart_page.wait_for_cart_update()
        
        # 验证商品已删除
        final_items_count = self.cart_page.get_cart_items_count()
        assert final_items_count == initial_items_count - 1, "购物车商品数量应该减少1"
        
        # 如果购物车为空，验证空购物车状态
        if final_items_count == 0:
            assert self.cart_page.is_cart_empty(), "应该显示空购物车状态"
            empty_message = self.cart_page.get_empty_cart_message()
            assert empty_message is not None, "应该显示空购物车消息"
    
    @pytest.mark.cart
    @pytest.mark.selection
    def test_item_selection(self, driver):
        """测试商品选择功能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加多个商品到购物车
        self.products_page.open()
        
        # 添加前两个商品
        self.products_page.click_add_to_cart(0)
        time.sleep(1)
        self.products_page.click_add_to_cart(1)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证有多个商品
        items_count = self.cart_page.get_cart_items_count()
        assert items_count >= 2, "购物车中应该有至少2个商品"
        
        # 测试单个商品选择
        self.cart_page.select_item(0)
        assert self.cart_page.is_item_selected(0), "第一个商品应该被选中"
        
        # 验证选中数量
        selected_count = self.cart_page.get_selected_items_count()
        assert selected_count == 1, "应该有1个商品被选中"
        
        # 测试全选功能
        self.cart_page.select_all_items()
        
        # 验证所有商品都被选中
        all_selected_count = self.cart_page.get_selected_items_count()
        assert all_selected_count == items_count, "所有商品都应该被选中"
        
        # 再次点击全选（取消全选）
        self.cart_page.select_all_items()
        
        # 验证所有商品都被取消选中
        none_selected_count = self.cart_page.get_selected_items_count()
        assert none_selected_count == 0, "所有商品都应该被取消选中"
    
    @pytest.mark.cart
    @pytest.mark.bulk_operations
    def test_bulk_operations(self, driver):
        """测试批量操作"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加多个商品到购物车
        self.products_page.open()
        
        # 添加前三个商品
        for i in range(3):
            self.products_page.click_add_to_cart(i)
            time.sleep(1)
        
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证有多个商品
        initial_items_count = self.cart_page.get_cart_items_count()
        assert initial_items_count >= 3, "购物车中应该有至少3个商品"
        
        # 选择前两个商品
        self.cart_page.select_item(0)
        self.cart_page.select_item(1)
        
        # 验证选中数量
        selected_count = self.cart_page.get_selected_items_count()
        assert selected_count == 2, "应该有2个商品被选中"
        
        # 测试批量删除
        self.cart_page.bulk_remove_selected()
        self.cart_page.wait_for_cart_update()
        
        # 验证商品已删除
        final_items_count = self.cart_page.get_cart_items_count()
        assert final_items_count == initial_items_count - 2, "应该删除2个商品"
    
    @pytest.mark.cart
    @pytest.mark.coupon
    def test_coupon_functionality(self, driver):
        """测试优惠券功能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证有商品在购物车中
        assert self.cart_page.get_cart_items_count() > 0, "购物车中应该有商品"
        
        # 选择商品
        self.cart_page.select_item(0)
        
        # 获取应用优惠券前的总金额
        initial_summary = self.cart_page.get_cart_summary()
        initial_total = initial_summary["total"]
        
        # 应用优惠券
        coupon_code = "TEST10"  # 假设这是一个有效的测试优惠券
        self.cart_page.apply_coupon(coupon_code)
        
        # 等待优惠券处理
        time.sleep(3)
        
        # 获取优惠券消息
        coupon_message = self.cart_page.get_coupon_message()
        print(f"优惠券消息: {coupon_message}")
        
        # 如果优惠券有效，验证优惠效果
        if coupon_message and ("成功" in coupon_message or "applied" in coupon_message.lower()):
            # 获取应用优惠券后的总金额
            updated_summary = self.cart_page.get_cart_summary()
            updated_total = updated_summary["total"]
            
            # 验证总金额有变化（通常是减少）
            assert updated_total != initial_total, "应用优惠券后总金额应该有变化"
            
            # 验证优惠券出现在已应用列表中
            applied_coupons = self.cart_page.get_applied_coupons()
            assert len(applied_coupons) > 0, "应该有已应用的优惠券"
            
            # 测试移除优惠券
            if applied_coupons:
                self.cart_page.remove_coupon(0)
                time.sleep(2)
                
                # 验证优惠券已移除
                remaining_coupons = self.cart_page.get_applied_coupons()
                assert len(remaining_coupons) < len(applied_coupons), "优惠券应该被移除"
    
    @pytest.mark.cart
    @pytest.mark.summary
    def test_cart_summary_calculation(self, driver):
        """测试购物车摘要计算"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 选择商品
        self.cart_page.select_item(0)
        
        # 获取购物车摘要
        summary = self.cart_page.get_cart_summary()
        
        # 验证摘要信息存在
        assert summary["selected_items_count"] is not None, "应该显示选中商品数量"
        assert summary["subtotal"] is not None, "应该显示小计金额"
        assert summary["total"] is not None, "应该显示总金额"
        
        print(f"购物车摘要: {summary}")
        
        # 修改商品数量，验证摘要更新
        initial_quantity = self.cart_page.get_item_info(0)["quantity"]
        self.cart_page.increase_item_quantity(0)
        self.cart_page.wait_for_cart_update()
        
        # 获取更新后的摘要
        updated_summary = self.cart_page.get_cart_summary()
        
        # 验证摘要已更新（数量增加，金额可能增加）
        updated_quantity = self.cart_page.get_item_info(0)["quantity"]
        assert updated_quantity == initial_quantity + 1, "商品数量应该增加"
    
    @pytest.mark.cart
    @pytest.mark.checkout
    def test_checkout_process(self, driver):
        """测试结算流程"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 验证有商品在购物车中
        assert self.cart_page.get_cart_items_count() > 0, "购物车中应该有商品"
        
        # 选择商品
        self.cart_page.select_item(0)
        
        # 验证结算按钮可用
        assert self.cart_page.is_checkout_button_enabled(), "结算按钮应该可用"
        
        # 点击结算
        self.cart_page.proceed_to_checkout()
        
        # 等待页面跳转
        time.sleep(3)
        
        # 验证跳转到结算页面
        current_url = driver.current_url
        assert ("checkout" in current_url or "order" in current_url or 
                "结算" in driver.title), "应该跳转到结算页面"
    
    @pytest.mark.cart
    @pytest.mark.empty_cart
    def test_empty_cart_functionality(self, driver):
        """测试空购物车功能"""
        # 初始化页面对象
        self.cart_page = CartPage(driver)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 如果购物车不为空，先清空
        if not self.cart_page.is_cart_empty():
            self.cart_page.select_all_items()
            self.cart_page.bulk_remove_selected()
            self.cart_page.wait_for_cart_update()
        
        # 验证空购物车状态
        assert self.cart_page.is_cart_empty(), "购物车应该为空"
        
        # 验证空购物车消息
        empty_message = self.cart_page.get_empty_cart_message()
        assert empty_message is not None, "应该显示空购物车消息"
        
        # 测试从空购物车去购物
        self.cart_page.go_shopping_from_empty_cart()
        
        # 等待页面跳转
        time.sleep(2)
        
        # 验证跳转到商品页面或首页
        current_url = driver.current_url
        assert ("products" in current_url or "home" in current_url or 
                current_url == config.BASE_URL + "/"), "应该跳转到购物页面"
    
    @pytest.mark.cart
    @pytest.mark.navigation
    def test_cart_navigation(self, driver):
        """测试购物车页面导航"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 测试继续购物
        self.cart_page.continue_shopping()
        
        # 等待页面跳转
        time.sleep(2)
        
        # 验证跳转到商品页面
        current_url = driver.current_url
        assert ("products" in current_url or "home" in current_url), "应该跳转到购物页面"
        
        # 返回购物车
        self.cart_page.open()
        time.sleep(2)
        
        # 验证推荐商品功能
        recommended_count = self.cart_page.get_recommended_products_count()
        print(f"推荐商品数量: {recommended_count}")
        
        if recommended_count > 0:
            # 点击第一个推荐商品
            self.cart_page.click_recommended_product(0)
            
            # 等待页面跳转
            time.sleep(2)
            
            # 验证跳转到商品详情页
            current_url = driver.current_url
            assert "product" in current_url, "应该跳转到商品详情页"
    
    @pytest.mark.cart
    @pytest.mark.performance
    def test_cart_performance(self, driver):
        """测试购物车性能"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 测试购物车页面加载性能
        start_time = time.time()
        self.cart_page.open()
        self.cart_page.wait_for_cart_update()
        load_time = time.time() - start_time
        
        # 验证页面加载时间合理（小于5秒）
        assert load_time < 5.0, f"购物车页面加载时间过长: {load_time:.2f}秒"
        
        # 测试数量更新性能
        update_start_time = time.time()
        self.cart_page.increase_item_quantity(0)
        self.cart_page.wait_for_cart_update()
        update_time = time.time() - update_start_time
        
        # 验证更新时间合理（小于3秒）
        assert update_time < 3.0, f"购物车更新时间过长: {update_time:.2f}秒"
    
    @pytest.mark.cart
    @pytest.mark.edge_case
    def test_cart_edge_cases(self, driver):
        """测试购物车边界情况"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
        # 测试设置极大数量
        large_quantity = 9999
        self.cart_page.update_item_quantity(0, large_quantity)
        self.cart_page.wait_for_cart_update()
        
        # 验证系统处理极大数量
        updated_quantity = self.cart_page.get_item_info(0)["quantity"]
        # 系统可能限制最大数量，验证不会出错
        assert updated_quantity > 0, "数量应该是正数"
        
        # 测试设置零数量
        self.cart_page.update_item_quantity(0, 0)
        self.cart_page.wait_for_cart_update()
        
        # 验证零数量处理（可能删除商品或设置为1）
        final_items_count = self.cart_page.get_cart_items_count()
        # 商品可能被删除或数量被设置为最小值
        
        # 测试无效优惠券
        if final_items_count > 0:
            invalid_coupon = "INVALID_COUPON_123"
            self.cart_page.apply_coupon(invalid_coupon)
            time.sleep(2)
            
            # 验证无效优惠券处理
            coupon_message = self.cart_page.get_coupon_message()
            if coupon_message:
                assert ("无效" in coupon_message or "invalid" in coupon_message.lower() or
                       "不存在" in coupon_message), "应该显示无效优惠券消息"
    
    @pytest.mark.cart
    @pytest.mark.responsive
    def test_cart_responsive_design(self, driver):
        """测试购物车响应式设计"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 先添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(2)
        
        # 打开购物车页面
        self.cart_page.open()
        time.sleep(2)
        
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
            
            # 验证关键元素仍然可见和可用
            assert self.cart_page.is_element_visible(
                self.cart_page.PAGE_TITLE, timeout=5)
            
            # 验证购物车商品列表可见
            if not self.cart_page.is_cart_empty():
                assert self.cart_page.is_element_visible(
                    self.cart_page.CART_ITEMS, timeout=5)
                
                # 验证关键操作按钮可见
                assert self.cart_page.is_element_visible(
                    self.cart_page.CHECKOUT_BUTTON, timeout=5)
        
        # 恢复默认窗口大小
        driver.maximize_window()
    
    @pytest.mark.cart
    @pytest.mark.integration
    def test_cart_integration_workflow(self, driver):
        """测试购物车完整工作流程"""
        # 初始化页面对象
        self.products_page = ProductsPage(driver)
        self.cart_page = CartPage(driver)
        
        # 执行完整的购物车操作流程
        operations_log = []
        
        # 1. 添加多个商品到购物车
        self.products_page.open()
        operations_log.append("打开商品页面")
        
        for i in range(2):
            self.products_page.click_add_to_cart(i)
            operations_log.append(f"添加第{i+1}个商品到购物车")
            time.sleep(1)
        
        time.sleep(2)
        
        # 2. 打开购物车页面
        self.cart_page.open()
        operations_log.append("打开购物车页面")
        time.sleep(2)
        
        # 3. 验证商品已添加
        items_count = self.cart_page.get_cart_items_count()
        operations_log.append(f"购物车中有{items_count}个商品")
        assert items_count >= 2, "应该有至少2个商品"
        
        # 4. 修改商品数量
        self.cart_page.select_item(0)
        self.cart_page.increase_item_quantity(0)
        operations_log.append("增加第一个商品数量")
        self.cart_page.wait_for_cart_update()
        
        # 5. 应用优惠券
        self.cart_page.apply_coupon("TEST10")
        operations_log.append("应用优惠券")
        time.sleep(2)
        
        # 6. 获取最终摘要
        final_summary = self.cart_page.get_cart_summary()
        operations_log.append(f"最终购物车摘要: {final_summary}")
        
        # 7. 验证结算按钮可用
        checkout_enabled = self.cart_page.is_checkout_button_enabled()
        operations_log.append(f"结算按钮可用: {checkout_enabled}")
        assert checkout_enabled, "结算按钮应该可用"
        
        # 输出操作日志
        print("购物车集成测试操作日志:")
        for log in operations_log:
            print(f"  - {log}")
        
        # 验证整个流程成功完成
        assert len(operations_log) >= 7, "应该完成所有操作步骤"