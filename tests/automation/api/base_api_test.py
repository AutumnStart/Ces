# -*- coding: utf-8 -*-
"""
API测试基础类
提供API测试的通用功能和设置
"""

import pytest
import time
from typing import Dict, Any
from .api_client import APIClient, APIResponse
from config.test_config import TestConfig


class BaseAPITest:
    """API测试基础类"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """
        API客户端fixture
        
        Returns:
            APIClient: API客户端实例
        """
        client = APIClient(TestConfig.BASE_URL)
        yield client
        client.close()
    
    @pytest.fixture(scope="function")
    def authenticated_client(self, api_client):
        """
        已认证的API客户端fixture
        
        Args:
            api_client: API客户端
            
        Returns:
            APIClient: 已认证的API客户端
        """
        # 登录获取会话
        test_user = TestConfig.TEST_USER
        response = api_client.login(test_user['username'], test_user['password'])
        
        # 检查登录是否成功
        if response.status_code not in [200, 302]:
            pytest.fail(f"管理员登录失败，状态码: {response.status_code}")
        
        # Flask会自动处理session cookie，无需手动设置
        
        yield api_client
        
        # 清理：登出
        try:
            api_client.logout()
        except:
            pass
    
    @pytest.fixture(scope="function")
    def admin_client(self, api_client):
        """
        管理员API客户端fixture
        
        Args:
            api_client: API客户端
            
        Returns:
            APIClient: 管理员API客户端
        """
        # 使用管理员账户登录
        admin_user = TestConfig.ADMIN_USER
        response = api_client.login(admin_user['username'], admin_user['password'])
        
        # 检查登录是否成功
        if response.status_code not in [200, 302]:
            pytest.fail(f"管理员登录失败，状态码: {response.status_code}")
        
        # Flask会自动处理session cookie，无需手动设置
        
        yield api_client
        
        # 清理：登出
        try:
            api_client.logout()
        except:
            pass
    
    def make_request_with_retry(self, client: APIClient, method: str, endpoint: str, 
                               max_retries: int = 3, delay: float = 1.0, **kwargs) -> APIResponse:
        """
        带重试机制的请求
        
        Args:
            client: API客户端
            method: HTTP方法
            endpoint: API端点
            max_retries: 最大重试次数
            delay: 重试延迟（秒）
            **kwargs: 其他请求参数
            
        Returns:
            APIResponse: 响应对象
            
        Raises:
            Exception: 重试次数用尽后抛出最后一次异常
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = client.get(endpoint, **kwargs)
                elif method.upper() == 'POST':
                    response = client.post(endpoint, **kwargs)
                elif method.upper() == 'PUT':
                    response = client.put(endpoint, **kwargs)
                elif method.upper() == 'DELETE':
                    response = client.delete(endpoint, **kwargs)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                return APIResponse(response)
                
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(delay)
                    continue
                else:
                    raise last_exception
    
    def assert_response_time(self, response: APIResponse, max_time: float = 2.0):
        """
        断言响应时间
        
        Args:
            response: API响应
            max_time: 最大响应时间（秒）
            
        Raises:
            AssertionError: 响应时间超过限制时抛出
        """
        response_time = response.response.elapsed.total_seconds()
        assert response_time <= max_time, f"响应时间过长: {response_time:.2f}秒 > {max_time}秒"
    
    def assert_response_headers(self, response: APIResponse, expected_headers: Dict[str, str]):
        """
        断言响应头
        
        Args:
            response: API响应
            expected_headers: 期望的响应头
            
        Raises:
            AssertionError: 响应头不匹配时抛出
        """
        for header, expected_value in expected_headers.items():
            actual_value = response.headers.get(header)
            assert actual_value == expected_value, f"响应头 '{header}' 不匹配，期望 '{expected_value}'，实际 '{actual_value}'"
    
    def assert_json_schema(self, response: APIResponse, expected_schema: Dict[str, Any]):
        """
        断言JSON响应结构
        
        Args:
            response: API响应
            expected_schema: 期望的JSON结构
            
        Raises:
            AssertionError: JSON结构不匹配时抛出
        """
        assert response.json_data is not None, "响应不是有效的JSON格式"
        
        def check_schema(data, schema, path=""):
            for key, expected_type in schema.items():
                current_path = f"{path}.{key}" if path else key
                
                assert key in data, f"JSON中缺少键: {current_path}"
                
                actual_value = data[key]
                
                if isinstance(expected_type, type):
                    assert isinstance(actual_value, expected_type), \
                        f"键 '{current_path}' 的类型不匹配，期望 {expected_type.__name__}，实际 {type(actual_value).__name__}"
                elif isinstance(expected_type, dict):
                    assert isinstance(actual_value, dict), \
                        f"键 '{current_path}' 应该是字典类型"
                    check_schema(actual_value, expected_type, current_path)
                elif isinstance(expected_type, list) and len(expected_type) > 0:
                    assert isinstance(actual_value, list), \
                        f"键 '{current_path}' 应该是列表类型"
                    if len(actual_value) > 0:
                        check_schema(actual_value[0], expected_type[0], f"{current_path}[0]")
        
        check_schema(response.json_data, expected_schema)
    
    def wait_for_condition(self, condition_func, timeout: float = 10.0, interval: float = 0.5) -> bool:
        """
        等待条件满足
        
        Args:
            condition_func: 条件函数
            timeout: 超时时间（秒）
            interval: 检查间隔（秒）
            
        Returns:
            bool: 条件是否在超时前满足
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    def create_test_data(self, client: APIClient, data_type: str, **kwargs) -> Dict[str, Any]:
        """
        创建测试数据
        
        Args:
            client: API客户端
            data_type: 数据类型
            **kwargs: 数据参数
            
        Returns:
            Dict[str, Any]: 创建的数据
        """
        # 这里可以根据不同的数据类型创建测试数据
        # 例如创建测试用户、测试商品等
        pass
    
    def cleanup_test_data(self, client: APIClient, data_id: str, data_type: str):
        """
        清理测试数据
        
        Args:
            client: API客户端
            data_id: 数据ID
            data_type: 数据类型
        """
        # 这里可以根据不同的数据类型清理测试数据
        pass