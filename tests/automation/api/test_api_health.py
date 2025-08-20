# -*- coding: utf-8 -*-
"""
API健康检查测试
测试API的基本可用性和健康状态
"""

import pytest
from .base_api_test import BaseAPITest
from .api_client import APIClient


class TestAPIHealth(BaseAPITest):
    """API健康检查测试类"""
    
    @pytest.mark.smoke
    def test_health_endpoint(self, api_client: APIClient):
        """
        测试健康检查端点
        
        Args:
            api_client: API客户端
        """
        # 发送健康检查请求
        response = api_client.get('/api/health')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应时间
        self.assert_response_time(response, max_time=3.0)
        
        # 验证响应内容
        json_data = response.json_data
        assert json_data is not None, "健康检查应返回JSON响应"
        assert 'status' in json_data, "响应中应包含status字段"
        assert json_data['status'] == 'healthy', "应用状态应为healthy"
    
    @pytest.mark.smoke
    def test_health_endpoint_response_structure(self, api_client: APIClient):
        """
        测试健康检查端点响应结构
        
        Args:
            api_client: API客户端
        """
        # 发送健康检查请求
        response = api_client.get('/api/health')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证JSON结构
        expected_schema = {
            'status': str,
            'timestamp': str
        }
        self.assert_json_schema(response, expected_schema)
    
    @pytest.mark.smoke
    def test_health_endpoint_headers(self, api_client: APIClient):
        """
        测试健康检查端点响应头
        
        Args:
            api_client: API客户端
        """
        # 发送健康检查请求
        response = api_client.get('/api/health')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应头
        expected_headers = {
            'Content-Type': 'application/json'
        }
        self.assert_response_headers(response, expected_headers)
    
    def test_health_endpoint_multiple_requests(self, api_client: APIClient):
        """
        测试健康检查端点的并发请求
        
        Args:
            api_client: API客户端
        """
        # 发送多个健康检查请求
        responses = []
        for i in range(5):
            response = api_client.get('/api/health')
            responses.append(response)
        
        # 验证所有响应
        for i, response in enumerate(responses):
            response.assert_status_code(200, f"第{i+1}个请求失败")
            
            json_data = response.json_data
            assert json_data is not None, f"第{i+1}个请求应返回JSON响应"
            assert json_data['status'] == 'healthy', f"第{i+1}个请求状态应为healthy"
    
    def test_health_endpoint_with_retry(self, api_client: APIClient):
        """
        测试健康检查端点的重试机制
        
        Args:
            api_client: API客户端
        """
        # 使用重试机制发送请求
        response = self.make_request_with_retry(
            client=api_client,
            method='GET',
            endpoint='/api/health',
            max_retries=3,
            delay=0.5
        )
        
        # 验证响应
        response.assert_status_code(200)
        assert response.json_data['status'] == 'healthy'