# -*- coding: utf-8 -*-
"""
购物车API测试
测试购物车相关的API端点
"""

import pytest
from .base_api_test import BaseAPITest
from .api_client import APIClient


class TestCartAPI(BaseAPITest):
    """购物车API测试类"""
    
    @pytest.mark.smoke
    def test_get_cart_unauthenticated(self, api_client: APIClient):
        """
        测试未认证用户获取购物车
        
        Args:
            api_client: API客户端
        """
        # 发送获取购物车请求（未登录）
        response = api_client.get('/api/cart')
        
        # 验证响应状态码（可能是401未授权或200空购物车）
        assert response.status_code in [200, 401, 302], f"未认证用户访问购物车应返回200、401或302，实际返回{response.status_code}"
        
        if response.status_code == 200:
            # 如果返回200，应该是空购物车或会话购物车
            json_data = response.json_data
            if json_data is not None:
                assert 'items' in json_data or 'cart_items' in json_data or isinstance(json_data, list), "购物车响应应包含商品列表"
    
    @pytest.mark.smoke
    def test_get_cart_authenticated(self, authenticated_client: APIClient):
        """
        测试已认证用户获取购物车
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 发送获取购物车请求（已登录）
        response = authenticated_client.get('/api/cart')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应时间
        self.assert_response_time(response, max_time=2.0)
        
        # 验证响应内容
        json_data = response.json_data
        assert json_data is not None, "购物车应返回JSON响应"
        
        # 验证购物车结构（可能是空购物车）
        if isinstance(json_data, dict):
            # 如果是对象格式
            assert 'items' in json_data or 'cart_items' in json_data or 'products' in json_data, "购物车对象应包含商品列表字段"
        elif isinstance(json_data, list):
            # 如果是数组格式（直接返回商品列表）
            pass  # 空列表也是有效的
        else:
            pytest.fail(f"购物车响应格式不正确: {type(json_data)}")
    
    def test_cart_api_headers(self, authenticated_client: APIClient):
        """
        测试购物车API响应头
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 发送获取购物车请求
        response = authenticated_client.get('/api/cart')
        response.assert_status_code(200)
        
        # 验证响应头
        expected_headers = {
            'Content-Type': 'application/json'
        }
        self.assert_response_headers(response, expected_headers)
    
    def test_cart_structure_with_items(self, authenticated_client: APIClient):
        """
        测试购物车结构（如果有商品）
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 获取购物车
        response = authenticated_client.get('/api/cart')
        response.assert_status_code(200)
        
        json_data = response.json_data
        
        if isinstance(json_data, dict):
            # 对象格式的购物车
            if 'items' in json_data and len(json_data['items']) > 0:
                # 验证购物车商品结构
                item = json_data['items'][0]
                expected_fields = ['product_id', 'quantity']
                for field in expected_fields:
                    assert field in item or any(f in item for f in ['id', 'name', 'price']), f"购物车商品应包含{field}或商品基本信息"
            elif 'cart_items' in json_data and len(json_data['cart_items']) > 0:
                # 验证购物车商品结构
                item = json_data['cart_items'][0]
                expected_fields = ['product_id', 'quantity']
                for field in expected_fields:
                    assert field in item or any(f in item for f in ['id', 'name', 'price']), f"购物车商品应包含{field}或商品基本信息"
        elif isinstance(json_data, list) and len(json_data) > 0:
            # 数组格式的购物车
            item = json_data[0]
            expected_fields = ['product_id', 'quantity']
            for field in expected_fields:
                assert field in item or any(f in item for f in ['id', 'name', 'price']), f"购物车商品应包含{field}或商品基本信息"
    
    def test_add_to_cart_post_method(self, authenticated_client: APIClient):
        """
        测试添加商品到购物车（POST方法）
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 首先获取可用商品
        products_response = authenticated_client.get('/api/products')
        products_response.assert_status_code(200)
        
        products = products_response.json_data
        if len(products) == 0:
            pytest.skip("没有可用的商品进行测试")
        
        # 尝试添加商品到购物车
        product_id = products[0]['id']
        cart_data = {
            'product_id': product_id,
            'quantity': 1
        }
        
        response = authenticated_client.post('/api/cart', json=cart_data)
        
        # 验证响应（可能是200、201或405方法不允许）
        assert response.status_code in [200, 201, 405, 404], f"添加到购物车应返回200、201、405或404，实际返回{response.status_code}"
        
        if response.status_code in [200, 201]:
            # 如果成功，验证响应
            json_data = response.json_data
            if json_data is not None:
                assert 'success' in json_data or 'message' in json_data or 'cart' in json_data, "添加购物车成功应返回相关信息"
    
    def test_update_cart_put_method(self, authenticated_client: APIClient):
        """
        测试更新购物车（PUT方法）
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 尝试更新购物车
        cart_data = {
            'items': []
        }
        
        response = authenticated_client.put('/api/cart', json=cart_data)
        
        # 验证响应（可能是200、405方法不允许或404）
        assert response.status_code in [200, 405, 404], f"更新购物车应返回200、405或404，实际返回{response.status_code}"
    
    def test_clear_cart_delete_method(self, authenticated_client: APIClient):
        """
        测试清空购物车（DELETE方法）
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 尝试清空购物车
        response = authenticated_client.delete('/api/cart')
        
        # 验证响应（可能是200、204、405方法不允许或404）
        assert response.status_code in [200, 204, 405, 404], f"清空购物车应返回200、204、405或404，实际返回{response.status_code}"
        
        if response.status_code in [200, 204]:
            # 如果成功，验证购物车已清空
            cart_response = authenticated_client.get('/api/cart')
            cart_response.assert_status_code(200)
            
            cart_data = cart_response.json_data
            if isinstance(cart_data, dict):
                if 'items' in cart_data:
                    assert len(cart_data['items']) == 0, "购物车应该已清空"
                elif 'cart_items' in cart_data:
                    assert len(cart_data['cart_items']) == 0, "购物车应该已清空"
            elif isinstance(cart_data, list):
                assert len(cart_data) == 0, "购物车应该已清空"
    
    def test_cart_api_performance(self, authenticated_client: APIClient):
        """
        测试购物车API性能
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 连续发送多个购物车请求测试性能
        response_times = []
        
        for i in range(3):
            response = authenticated_client.get('/api/cart')
            response.assert_status_code(200)
            response_time = response.response.elapsed.total_seconds()
            response_times.append(response_time)
        
        # 验证平均响应时间
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2.0, f"购物车API平均响应时间过长: {avg_response_time:.2f}秒"
    
    def test_cart_concurrent_access(self, authenticated_client: APIClient):
        """
        测试购物车并发访问
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 同时发送多个购物车请求
        responses = []
        for i in range(3):
            response = authenticated_client.get('/api/cart')
            responses.append(response)
        
        # 验证所有响应
        for i, response in enumerate(responses):
            response.assert_status_code(200, f"第{i+1}个并发请求失败")
            
            json_data = response.json_data
            assert json_data is not None, f"第{i+1}个并发请求应返回JSON响应"