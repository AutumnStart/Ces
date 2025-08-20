# -*- coding: utf-8 -*-
"""
产品API测试
测试商品相关的API端点
"""

import pytest
from .base_api_test import BaseAPITest
from .api_client import APIClient


class TestProductsAPI(BaseAPITest):
    """产品API测试类"""
    
    @pytest.mark.smoke
    def test_get_products_list(self, api_client: APIClient):
        """
        测试获取商品列表
        
        Args:
            api_client: API客户端
        """
        # 发送获取商品列表请求
        response = api_client.get('/api/products')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应时间
        self.assert_response_time(response, max_time=2.0)
        
        # 验证响应内容
        json_data = response.json_data
        assert json_data is not None, "商品列表应返回JSON响应"
        assert isinstance(json_data, list), "商品列表应为数组格式"
        
        # 如果有商品，验证商品结构
        if len(json_data) > 0:
            product = json_data[0]
            required_fields = ['id', 'name', 'price', 'description']
            for field in required_fields:
                assert field in product, f"商品对象应包含{field}字段"
    
    @pytest.mark.smoke
    def test_get_products_list_structure(self, api_client: APIClient):
        """
        测试商品列表响应结构
        
        Args:
            api_client: API客户端
        """
        # 发送获取商品列表请求
        response = api_client.get('/api/products')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证JSON结构
        json_data = response.json_data
        assert isinstance(json_data, list), "商品列表应为数组格式"
        
        # 如果有商品，验证第一个商品的结构
        if len(json_data) > 0:
            expected_schema = [{
                'id': int,
                'name': str,
                'price': (int, float),
                'description': str
            }]
            self.assert_json_schema({'products': json_data}, {'products': expected_schema})
    
    def test_get_product_detail_valid_id(self, api_client: APIClient):
        """
        测试获取有效商品详情
        
        Args:
            api_client: API客户端
        """
        # 首先获取商品列表
        products_response = api_client.get('/api/products')
        products_response.assert_status_code(200)
        
        products = products_response.json_data
        if len(products) == 0:
            pytest.skip("没有可用的商品进行测试")
        
        # 获取第一个商品的详情
        product_id = products[0]['id']
        response = api_client.get(f'/api/products/{product_id}')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应时间
        self.assert_response_time(response, max_time=1.5)
        
        # 验证响应内容
        json_data = response.json_data
        assert json_data is not None, "商品详情应返回JSON响应"
        assert json_data['id'] == product_id, "返回的商品ID应与请求的ID一致"
        
        # 验证必需字段
        required_fields = ['id', 'name', 'price', 'description']
        for field in required_fields:
            assert field in json_data, f"商品详情应包含{field}字段"
    
    def test_get_product_detail_invalid_id(self, api_client: APIClient):
        """
        测试获取无效商品详情
        
        Args:
            api_client: API客户端
        """
        # 使用不存在的商品ID
        invalid_id = 99999
        response = api_client.get(f'/api/products/{invalid_id}')
        
        # 验证响应状态码（应该是404）
        response.assert_status_code(404)
    
    def test_get_product_detail_invalid_format(self, api_client: APIClient):
        """
        测试使用无效格式的商品ID
        
        Args:
            api_client: API客户端
        """
        # 使用非数字的商品ID
        invalid_id = "abc"
        response = api_client.get(f'/api/products/{invalid_id}')
        
        # 验证响应状态码（应该是404或400）
        assert response.status_code in [400, 404], f"无效ID格式应返回400或404状态码，实际返回{response.status_code}"
    
    def test_products_api_headers(self, api_client: APIClient):
        """
        测试商品API响应头
        
        Args:
            api_client: API客户端
        """
        # 测试商品列表API响应头
        response = api_client.get('/api/products')
        response.assert_status_code(200)
        
        # 验证响应头
        expected_headers = {
            'Content-Type': 'application/json'
        }
        self.assert_response_headers(response, expected_headers)
    
    def test_products_api_pagination(self, api_client: APIClient):
        """
        测试商品API分页功能（如果支持）
        
        Args:
            api_client: API客户端
        """
        # 测试带分页参数的请求
        response = api_client.get('/api/products', params={'page': 1, 'limit': 5})
        
        # 即使不支持分页，也应该返回正常响应
        response.assert_status_code(200)
        
        json_data = response.json_data
        assert isinstance(json_data, list), "即使有分页参数，也应返回商品列表"
    
    def test_products_api_search(self, api_client: APIClient):
        """
        测试商品搜索功能（如果支持）
        
        Args:
            api_client: API客户端
        """
        # 测试带搜索参数的请求
        response = api_client.get('/api/products', params={'search': 'test'})
        
        # 即使不支持搜索，也应该返回正常响应
        response.assert_status_code(200)
        
        json_data = response.json_data
        assert isinstance(json_data, list), "即使有搜索参数，也应返回商品列表"
    
    def test_products_api_performance(self, api_client: APIClient):
        """
        测试商品API性能
        
        Args:
            api_client: API客户端
        """
        # 连续发送多个请求测试性能
        response_times = []
        
        for i in range(5):
            response = api_client.get('/api/products')
            response.assert_status_code(200)
            response_time = response.response.elapsed.total_seconds()
            response_times.append(response_time)
        
        # 验证平均响应时间
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2.0, f"平均响应时间过长: {avg_response_time:.2f}秒"
        
        # 验证最大响应时间
        max_response_time = max(response_times)
        assert max_response_time < 3.0, f"最大响应时间过长: {max_response_time:.2f}秒"