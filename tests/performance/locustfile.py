#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商城系统负载测试
使用 Locust 进行性能和负载测试

安装依赖:
pip install locust

运行方式:
locust -f locustfile.py --host=http://localhost:5000

或者使用Web界面:
locust -f locustfile.py --host=http://localhost:5000 --web-host=0.0.0.0 --web-port=8089
"""

import random
import time
from locust import HttpUser, task, between
from locust.exception import RescheduleTask


class ShopUser(HttpUser):
    """
    模拟商城用户行为的负载测试类
    """
    
    # 用户请求间隔时间（秒）
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        用户开始测试时的初始化操作
        """
        self.session_id = None
        self.is_logged_in = False
        self.user_credentials = {
            'username': f'testuser_{random.randint(1000, 9999)}',
            'password': 'test123'
        }
        
        # 尝试登录
        self.login()
    
    def login(self):
        """
        用户登录操作
        """
        try:
            # 首先访问登录页面
            response = self.client.get('/login', name='访问登录页面')
            
            if response.status_code == 200:
                # 尝试登录
                login_data = {
                    'username': 'admin',  # 使用已知的管理员账号
                    'password': 'admin123'
                }
                
                response = self.client.post(
                    '/login',
                    data=login_data,
                    name='用户登录',
                    allow_redirects=False
                )
                
                # 检查登录是否成功（302重定向表示成功）
                if response.status_code == 302:
                    self.is_logged_in = True
                    print(f"用户登录成功: {login_data['username']}")
                else:
                    print(f"用户登录失败: {response.status_code}")
                    
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
    
    @task(10)
    def view_homepage(self):
        """
        访问首页 - 高频操作
        """
        with self.client.get('/', catch_response=True, name='访问首页') as response:
            if response.status_code == 200:
                if '商城系统' in response.text or 'Shop' in response.text:
                    response.success()
                else:
                    response.failure('首页内容不正确')
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(8)
    def view_products(self):
        """
        查看商品列表 - 高频操作
        """
        with self.client.get('/products', catch_response=True, name='查看商品列表') as response:
            if response.status_code == 200:
                if '商品' in response.text or 'Product' in response.text:
                    response.success()
                else:
                    response.failure('商品页面内容不正确')
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(6)
    def view_product_detail(self):
        """
        查看商品详情 - 中频操作
        """
        # 模拟查看不同商品的详情
        product_id = random.randint(1, 10)
        
        with self.client.get(f'/products/{product_id}', catch_response=True, name='查看商品详情') as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 商品不存在是正常情况
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(4)
    def search_products(self):
        """
        搜索商品 - 中频操作
        """
        search_terms = ['手机', '电脑', '耳机', '键盘', '鼠标', 'phone', 'laptop']
        search_term = random.choice(search_terms)
        
        with self.client.get(f'/products?search={search_term}', catch_response=True, name='搜索商品') as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(3)
    def add_to_cart(self):
        """
        添加商品到购物车 - 中频操作
        """
        if not self.is_logged_in:
            return
        
        product_id = random.randint(1, 10)
        quantity = random.randint(1, 3)
        
        cart_data = {
            'product_id': product_id,
            'quantity': quantity
        }
        
        with self.client.post('/cart/add', data=cart_data, catch_response=True, name='添加到购物车') as response:
            if response.status_code in [200, 302, 404]:  # 404表示商品不存在，也是正常情况
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(2)
    def view_cart(self):
        """
        查看购物车 - 低频操作
        """
        if not self.is_logged_in:
            return
        
        with self.client.get('/cart', catch_response=True, name='查看购物车') as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(1)
    def user_profile(self):
        """
        查看用户资料 - 低频操作
        """
        if not self.is_logged_in:
            return
        
        with self.client.get('/profile', catch_response=True, name='查看用户资料') as response:
            if response.status_code in [200, 404]:  # 可能没有实现用户资料页面
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    def on_stop(self):
        """
        用户停止测试时的清理操作
        """
        if self.is_logged_in:
            try:
                # 尝试登出
                self.client.post('/logout', name='用户登出')
            except:
                pass


class AdminUser(HttpUser):
    """
    模拟管理员用户行为的负载测试类
    """
    
    wait_time = between(2, 5)
    weight = 1  # 管理员用户权重较低
    
    def on_start(self):
        """
        管理员用户初始化
        """
        self.is_logged_in = False
        self.admin_login()
    
    def admin_login(self):
        """
        管理员登录
        """
        try:
            response = self.client.get('/login', name='管理员访问登录页面')
            
            if response.status_code == 200:
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                
                response = self.client.post(
                    '/login',
                    data=login_data,
                    name='管理员登录',
                    allow_redirects=False
                )
                
                if response.status_code == 302:
                    self.is_logged_in = True
                    print("管理员登录成功")
                    
        except Exception as e:
            print(f"管理员登录错误: {e}")
    
    @task(5)
    def admin_dashboard(self):
        """
        访问管理员仪表板
        """
        if not self.is_logged_in:
            return
        
        with self.client.get('/admin', catch_response=True, name='管理员仪表板') as response:
            if response.status_code in [200, 404]:  # 可能没有实现管理员页面
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(3)
    def manage_products(self):
        """
        管理商品
        """
        if not self.is_logged_in:
            return
        
        with self.client.get('/admin/products', catch_response=True, name='管理商品') as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(2)
    def view_orders(self):
        """
        查看订单
        """
        if not self.is_logged_in:
            return
        
        with self.client.get('/admin/orders', catch_response=True, name='查看订单') as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')


class QuickTestUser(HttpUser):
    """
    快速测试用户 - 用于快速验证系统基本功能
    """
    
    wait_time = between(0.5, 1)
    weight = 3  # 较高权重，用于快速测试
    
    @task(1)
    def quick_health_check(self):
        """
        快速健康检查
        """
        endpoints = ['/', '/products', '/login']
        
        for endpoint in endpoints:
            with self.client.get(endpoint, catch_response=True, name=f'健康检查-{endpoint}') as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f'{endpoint} 状态码错误: {response.status_code}')
            
            # 短暂延迟
            time.sleep(0.1)


# 自定义负载测试场景
class StressTestUser(HttpUser):
    """
    压力测试用户 - 用于压力测试场景
    """
    
    wait_time = between(0.1, 0.5)  # 更短的等待时间
    weight = 2
    
    @task(1)
    def stress_homepage(self):
        """
        压力测试首页
        """
        with self.client.get('/', catch_response=True, name='压力测试-首页') as response:
            if response.status_code == 200:
                # 检查响应时间
                if response.elapsed.total_seconds() > 2.0:
                    response.failure(f'响应时间过长: {response.elapsed.total_seconds()}秒')
                else:
                    response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')
    
    @task(1)
    def stress_products(self):
        """
        压力测试商品页面
        """
        with self.client.get('/products', catch_response=True, name='压力测试-商品页面') as response:
            if response.status_code == 200:
                if response.elapsed.total_seconds() > 3.0:
                    response.failure(f'响应时间过长: {response.elapsed.total_seconds()}秒')
                else:
                    response.success()
            else:
                response.failure(f'状态码错误: {response.status_code}')


if __name__ == '__main__':
    # 可以在这里添加一些配置或测试代码
    print("Locust 负载测试文件已准备就绪")
    print("运行命令: locust -f locustfile.py --host=http://localhost:5000")
    print("Web界面: locust -f locustfile.py --host=http://localhost:5000 --web-host=0.0.0.0 --web-port=8089")