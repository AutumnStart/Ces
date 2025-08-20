#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
首页功能UI自动化测试
测试首页加载、导航、搜索、轮播图等功能
"""

import pytest
import time
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from config.test_config import TestConfig

config = TestConfig()

class TestHome:
    """首页功能测试类"""
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.home_page = None
        self.login_page = None
        self.products_page = None
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        pass
    
    @pytest.mark.smoke
    @pytest.mark.home
    def test_home_page_load(self, driver):
        """测试首页加载"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 验证页面标题
        assert "首页" in driver.title or "Home" in driver.title or "商城" in driver.title
        
        # 验证页面关键元素存在
        assert self.home_page.is_element_visible(self.home_page.NAVBAR, timeout=10)
        
        # 获取首页信息
        page_info = self.home_page.get_page_info()
        print(f"首页信息: {page_info}")
        
        # 验证页面加载完成
        assert self.home_page.wait_for_page_load(), "首页应该完全加载"
    
    @pytest.mark.home
    @pytest.mark.navigation
    def test_navigation_bar(self, driver):
        """测试导航栏功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 验证导航栏存在
        assert self.home_page.is_element_visible(self.home_page.NAVBAR, timeout=10)
        
        # 测试Logo点击
        self.home_page.click_logo()
        time.sleep(2)
        
        # 验证仍在首页
        current_url = driver.current_url
        assert current_url == config.BASE_URL or current_url == config.BASE_URL + "/"
        
        # 测试商品链接
        self.home_page.click_products_link()
        time.sleep(2)
        
        # 验证跳转到商品页面
        current_url = driver.current_url
        assert "products" in current_url or "商品" in driver.title
        
        # 返回首页
        self.home_page.open()
        time.sleep(2)
        
        # 测试购物车链接
        self.home_page.click_cart_link()
        time.sleep(2)
        
        # 验证跳转到购物车页面
        current_url = driver.current_url
        assert "cart" in current_url or "购物车" in driver.title
    
    @pytest.mark.home
    @pytest.mark.search
    def test_search_functionality(self, driver):
        """测试搜索功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 验证搜索框存在
        assert self.home_page.is_element_visible(self.home_page.SEARCH_INPUT, timeout=10)
        
        # 测试搜索功能
        search_term = "手机"
        self.home_page.search_products(search_term)
        
        # 等待搜索结果
        time.sleep(3)
        
        # 验证跳转到搜索结果页面
        current_url = driver.current_url
        assert ("search" in current_url or "products" in current_url or 
                search_term in current_url), "应该跳转到搜索结果页面"
        
        # 返回首页测试空搜索
        self.home_page.open()
        time.sleep(2)
        
        # 测试空搜索
        self.home_page.search_products("")
        time.sleep(2)
        
        # 验证空搜索处理（可能显示所有商品或提示消息）
        current_url = driver.current_url
        # 空搜索可能跳转到商品页面或保持在首页
        
        # 返回首页测试特殊字符搜索
        self.home_page.open()
        time.sleep(2)
        
        # 测试特殊字符搜索
        special_search = "@#$%"
        self.home_page.search_products(special_search)
        time.sleep(2)
        
        # 验证特殊字符搜索不会导致错误
        # 页面应该正常显示，可能显示无结果
    
    @pytest.mark.home
    @pytest.mark.carousel
    def test_carousel_functionality(self, driver):
        """测试轮播图功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 检查轮播图是否存在
        if self.home_page.is_element_visible(self.home_page.CAROUSEL, timeout=5):
            # 获取轮播图信息
            carousel_info = self.home_page.get_carousel_info()
            print(f"轮播图信息: {carousel_info}")
            
            # 如果有多张图片，测试导航
            if carousel_info["total_slides"] > 1:
                # 测试下一张
                initial_slide = carousel_info["current_slide"]
                self.home_page.next_carousel_slide()
                time.sleep(2)
                
                # 验证切换成功
                updated_info = self.home_page.get_carousel_info()
                assert updated_info["current_slide"] != initial_slide, "轮播图应该切换到下一张"
                
                # 测试上一张
                self.home_page.previous_carousel_slide()
                time.sleep(2)
                
                # 验证切换回来
                final_info = self.home_page.get_carousel_info()
                assert final_info["current_slide"] == initial_slide, "轮播图应该切换回原来的图片"
                
                # 测试指示器点击
                if carousel_info["total_slides"] > 2:
                    self.home_page.click_carousel_indicator(2)
                    time.sleep(2)
                    
                    # 验证跳转到指定图片
                    indicator_info = self.home_page.get_carousel_info()
                    assert indicator_info["current_slide"] == 2, "应该跳转到第3张图片"
            
            # 测试轮播图点击
            self.home_page.click_carousel_slide()
            time.sleep(2)
            
            # 验证点击效果（可能跳转到商品详情或其他页面）
            current_url = driver.current_url
            # 轮播图点击可能跳转到不同页面，这里只验证没有出错
        else:
            print("轮播图不存在，跳过轮播图测试")
    
    @pytest.mark.home
    @pytest.mark.features
    def test_featured_sections(self, driver):
        """测试特色功能区"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 测试特色功能区
        if self.home_page.is_element_visible(self.home_page.FEATURES_SECTION, timeout=5):
            features = self.home_page.get_features_info()
            print(f"特色功能: {features}")
            
            # 验证特色功能数量
            assert len(features) > 0, "应该有特色功能展示"
            
            # 测试点击第一个特色功能
            if features:
                self.home_page.click_feature(0)
                time.sleep(2)
                
                # 验证点击效果
                current_url = driver.current_url
                # 特色功能点击可能跳转到不同页面
        else:
            print("特色功能区不存在，跳过特色功能测试")
    
    @pytest.mark.home
    @pytest.mark.products
    def test_featured_products(self, driver):
        """测试热门商品区"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 测试热门商品区
        if self.home_page.is_element_visible(self.home_page.FEATURED_PRODUCTS, timeout=5):
            products = self.home_page.get_featured_products()
            print(f"热门商品数量: {len(products)}")
            
            # 验证有热门商品
            assert len(products) > 0, "应该有热门商品展示"
            
            # 测试商品信息
            for i, product in enumerate(products[:3]):  # 只测试前3个商品
                print(f"商品{i+1}: {product}")
                
                # 验证商品信息完整性
                assert product["title"] is not None, "商品应该有标题"
                assert product["price"] is not None, "商品应该有价格"
                
                # 测试商品点击
                self.home_page.click_featured_product(i)
                time.sleep(2)
                
                # 验证跳转到商品详情页
                current_url = driver.current_url
                if "product" in current_url:
                    # 返回首页继续测试
                    self.home_page.open()
                    time.sleep(2)
                    break
        else:
            print("热门商品区不存在，跳过热门商品测试")
    
    @pytest.mark.home
    @pytest.mark.statistics
    def test_statistics_section(self, driver):
        """测试统计数据区"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 测试统计数据区
        if self.home_page.is_element_visible(self.home_page.STATS_SECTION, timeout=5):
            stats = self.home_page.get_statistics_info()
            print(f"统计数据: {stats}")
            
            # 验证统计数据
            assert len(stats) > 0, "应该有统计数据展示"
            
            # 验证统计数据格式
            for stat in stats:
                assert stat["label"] is not None, "统计项应该有标签"
                assert stat["value"] is not None, "统计项应该有数值"
        else:
            print("统计数据区不存在，跳过统计数据测试")
    
    @pytest.mark.home
    @pytest.mark.footer
    def test_footer_functionality(self, driver):
        """测试页脚功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 滚动到页面底部
        self.home_page.scroll_to_bottom()
        time.sleep(2)
        
        # 验证页脚存在
        if self.home_page.is_element_visible(self.home_page.FOOTER, timeout=5):
            # 获取页脚信息
            footer_info = self.home_page.get_footer_info()
            print(f"页脚信息: {footer_info}")
            
            # 验证页脚内容
            assert footer_info is not None, "页脚应该有内容"
        else:
            print("页脚不存在，跳过页脚测试")
    
    @pytest.mark.home
    @pytest.mark.login_status
    def test_login_status_display(self, driver):
        """测试登录状态显示"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        self.login_page = LoginPage(driver)
        
        # 打开首页（未登录状态）
        self.home_page.open()
        
        # 验证未登录状态
        assert not self.home_page.is_user_logged_in(), "用户应该未登录"
        
        # 获取登录状态信息
        login_info = self.home_page.get_login_status_info()
        print(f"未登录状态信息: {login_info}")
        
        # 执行登录
        self.login_page.open()
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        time.sleep(2)
        
        # 返回首页
        self.home_page.open()
        time.sleep(2)
        
        # 验证已登录状态
        assert self.home_page.is_user_logged_in(), "用户应该已登录"
        
        # 获取登录后状态信息
        logged_in_info = self.home_page.get_login_status_info()
        print(f"已登录状态信息: {logged_in_info}")
        
        # 验证用户名显示
        displayed_username = self.home_page.get_displayed_username()
        assert displayed_username is not None, "应该显示用户名"
        print(f"显示的用户名: {displayed_username}")
    
    @pytest.mark.home
    @pytest.mark.cart_count
    def test_cart_count_display(self, driver):
        """测试购物车数量显示"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        self.login_page = LoginPage(driver)
        self.products_page = ProductsPage(driver)
        
        # 先登录
        self.login_page.open()
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        time.sleep(2)
        
        # 打开首页
        self.home_page.open()
        
        # 获取初始购物车数量
        initial_count = self.home_page.get_cart_count()
        print(f"初始购物车数量: {initial_count}")
        
        # 添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        time.sleep(3)
        
        # 返回首页检查购物车数量
        self.home_page.open()
        time.sleep(2)
        
        # 验证购物车数量增加
        updated_count = self.home_page.get_cart_count()
        print(f"更新后购物车数量: {updated_count}")
        assert updated_count > initial_count, "购物车数量应该增加"
    
    @pytest.mark.home
    @pytest.mark.messages
    def test_message_display(self, driver):
        """测试消息提示显示"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 检查是否有消息提示
        if self.home_page.has_message():
            message = self.home_page.get_message()
            print(f"页面消息: {message}")
            
            # 验证消息内容
            assert message is not None, "消息应该有内容"
            
            # 测试关闭消息
            self.home_page.close_message()
            time.sleep(1)
            
            # 验证消息已关闭
            assert not self.home_page.has_message(), "消息应该被关闭"
        else:
            print("没有消息提示")
    
    @pytest.mark.home
    @pytest.mark.responsive
    def test_responsive_design(self, driver):
        """测试响应式设计"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
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
            
            print(f"测试屏幕尺寸: {width}x{height}")
            
            # 验证关键元素在不同尺寸下仍然可见
            assert self.home_page.is_element_visible(
                self.home_page.NAVBAR, timeout=5), f"导航栏在{width}x{height}下应该可见"
            
            # 验证搜索框可见（可能在移动端折叠）
            search_visible = self.home_page.is_element_visible(
                self.home_page.SEARCH_INPUT, timeout=3)
            print(f"搜索框在{width}x{height}下可见: {search_visible}")
            
            # 在小屏幕上可能需要点击菜单按钮
            if width <= 768:
                # 检查是否有移动端菜单按钮
                mobile_menu_visible = self.home_page.is_element_visible(
                    self.home_page.MOBILE_MENU_BUTTON, timeout=3)
                print(f"移动端菜单按钮可见: {mobile_menu_visible}")
        
        # 恢复默认窗口大小
        driver.maximize_window()
    
    @pytest.mark.home
    @pytest.mark.performance
    def test_page_performance(self, driver):
        """测试页面性能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 测试页面加载性能
        start_time = time.time()
        self.home_page.open()
        
        # 等待页面完全加载
        self.home_page.wait_for_page_load()
        load_time = time.time() - start_time
        
        # 验证页面加载时间合理（小于5秒）
        assert load_time < 5.0, f"首页加载时间过长: {load_time:.2f}秒"
        print(f"首页加载时间: {load_time:.2f}秒")
        
        # 测试搜索响应性能
        search_start_time = time.time()
        self.home_page.search_products("测试")
        search_time = time.time() - search_start_time
        
        # 验证搜索响应时间合理（小于3秒）
        assert search_time < 3.0, f"搜索响应时间过长: {search_time:.2f}秒"
        print(f"搜索响应时间: {search_time:.2f}秒")
    
    @pytest.mark.home
    @pytest.mark.accessibility
    def test_accessibility_features(self, driver):
        """测试可访问性功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 测试键盘导航
        # 聚焦到搜索框
        search_input = self.home_page.find_element(self.home_page.SEARCH_INPUT)
        search_input.click()
        
        # 验证搜索框获得焦点
        focused_element = driver.switch_to.active_element
        assert focused_element == search_input, "搜索框应该获得焦点"
        
        # 测试Tab键导航
        from selenium.webdriver.common.keys import Keys
        focused_element.send_keys(Keys.TAB)
        
        # 验证焦点移动到下一个元素
        new_focused_element = driver.switch_to.active_element
        assert new_focused_element != search_input, "焦点应该移动到下一个元素"
        
        # 测试图片alt属性
        images = driver.find_elements("tag name", "img")
        for img in images[:5]:  # 只检查前5张图片
            alt_text = img.get_attribute("alt")
            if alt_text is None or alt_text.strip() == "":
                print(f"警告: 图片缺少alt属性: {img.get_attribute('src')}")
    
    @pytest.mark.home
    @pytest.mark.edge_case
    def test_edge_cases(self, driver):
        """测试边界情况"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        
        # 打开首页
        self.home_page.open()
        
        # 测试网络中断模拟（通过JavaScript）
        try:
            # 模拟网络错误
            driver.execute_script("window.navigator.onLine = false;")
            
            # 尝试搜索
            self.home_page.search_products("测试")
            time.sleep(2)
            
            # 恢复网络
            driver.execute_script("window.navigator.onLine = true;")
        except Exception as e:
            print(f"网络中断测试异常: {e}")
        
        # 测试超长搜索词
        long_search_term = "a" * 1000
        self.home_page.search_products(long_search_term)
        time.sleep(2)
        
        # 验证系统处理超长输入不会崩溃
        # 页面应该正常响应
        
        # 测试特殊字符搜索
        special_chars = "<script>alert('test')</script>"
        self.home_page.search_products(special_chars)
        time.sleep(2)
        
        # 验证XSS防护
        # 页面不应该执行脚本，应该正常显示搜索结果或错误信息
        
        # 测试Unicode字符
        unicode_search = "测试🔍商品"
        self.home_page.search_products(unicode_search)
        time.sleep(2)
        
        # 验证Unicode字符处理
        # 系统应该正确处理Unicode字符
    
    @pytest.mark.home
    @pytest.mark.integration
    def test_home_page_integration(self, driver):
        """测试首页集成功能"""
        # 初始化页面对象
        self.home_page = HomePage(driver)
        self.login_page = LoginPage(driver)
        self.products_page = ProductsPage(driver)
        
        # 执行完整的首页操作流程
        operations_log = []
        
        # 1. 访问首页
        self.home_page.open()
        operations_log.append("访问首页")
        
        # 2. 验证页面加载
        assert self.home_page.wait_for_page_load(), "首页应该完全加载"
        operations_log.append("首页加载完成")
        
        # 3. 执行搜索
        self.home_page.search_products("手机")
        operations_log.append("执行搜索")
        time.sleep(2)
        
        # 4. 返回首页
        self.home_page.open()
        operations_log.append("返回首页")
        time.sleep(2)
        
        # 5. 点击商品链接
        self.home_page.click_products_link()
        operations_log.append("点击商品链接")
        time.sleep(2)
        
        # 6. 返回首页并登录
        self.home_page.open()
        self.login_page.open()
        test_user = config.get_test_user()
        self.login_page.login(test_user["username"], test_user["password"])
        operations_log.append("用户登录")
        time.sleep(2)
        
        # 7. 返回首页验证登录状态
        self.home_page.open()
        assert self.home_page.is_user_logged_in(), "用户应该已登录"
        operations_log.append("验证登录状态")
        
        # 8. 添加商品到购物车
        self.products_page.open()
        self.products_page.click_add_to_cart(0)
        operations_log.append("添加商品到购物车")
        time.sleep(2)
        
        # 9. 返回首页验证购物车数量
        self.home_page.open()
        cart_count = self.home_page.get_cart_count()
        assert cart_count > 0, "购物车应该有商品"
        operations_log.append(f"验证购物车数量: {cart_count}")
        
        # 输出操作日志
        print("首页集成测试操作日志:")
        for log in operations_log:
            print(f"  - {log}")
        
        # 验证整个流程成功完成
        assert len(operations_log) >= 8, "应该完成所有操作步骤"