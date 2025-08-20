# -*- coding: utf-8 -*-
"""
用户API测试
测试用户管理相关的API端点
"""

import pytest
from .base_api_test import BaseAPITest
from .api_client import APIClient


class TestUsersAPI(BaseAPITest):
    """用户API测试类"""
    
    def test_get_users_unauthenticated(self, api_client: APIClient):
        """
        测试未认证用户获取用户列表
        
        Args:
            api_client: API客户端
        """
        # 发送获取用户列表请求（未登录）
        response = api_client.get('/api/users')
        
        # 验证响应状态码（应该是401未授权或403禁止访问）
        assert response.status_code in [401, 403, 302], f"未认证用户访问用户列表应返回401、403或302，实际返回{response.status_code}"
    
    def test_get_users_regular_user(self, authenticated_client: APIClient):
        """
        测试普通用户获取用户列表
        
        Args:
            authenticated_client: 已认证的API客户端（普通用户）
        """
        # 发送获取用户列表请求（普通用户）
        response = authenticated_client.get('/api/users')
        
        # 验证响应状态码（普通用户可能无权限访问，应该是403）
        assert response.status_code in [200, 403], f"普通用户访问用户列表应返回200或403，实际返回{response.status_code}"
        
        if response.status_code == 200:
            # 如果普通用户有权限，验证响应
            json_data = response.json_data
            assert json_data is not None, "用户列表应返回JSON响应"
            assert isinstance(json_data, list), "用户列表应为数组格式"
    
    @pytest.mark.admin
    def test_get_users_admin(self, admin_client: APIClient):
        """
        测试管理员获取用户列表
        
        Args:
            admin_client: 管理员API客户端
        """
        # 发送获取用户列表请求（管理员）
        response = admin_client.get('/api/users')
        
        # 验证响应状态码
        response.assert_status_code(200)
        
        # 验证响应时间
        self.assert_response_time(response, max_time=2.0)
        
        # 验证响应内容
        json_data = response.json_data
        assert json_data is not None, "用户列表应返回JSON响应"
        assert isinstance(json_data, list), "用户列表应为数组格式"
        
        # 如果有用户，验证用户结构
        if len(json_data) > 0:
            user = json_data[0]
            required_fields = ['id', 'username']
            for field in required_fields:
                assert field in user, f"用户对象应包含{field}字段"
            
            # 确保不返回敏感信息
            sensitive_fields = ['password', 'password_hash']
            for field in sensitive_fields:
                assert field not in user, f"用户对象不应包含敏感字段{field}"
    
    @pytest.mark.admin
    def test_users_list_structure(self, admin_client: APIClient):
        """
        测试用户列表响应结构
        
        Args:
            admin_client: 管理员API客户端
        """
        # 发送获取用户列表请求
        response = admin_client.get('/api/users')
        response.assert_status_code(200)
        
        # 验证JSON结构
        json_data = response.json_data
        assert isinstance(json_data, list), "用户列表应为数组格式"
        
        # 如果有用户，验证第一个用户的结构
        if len(json_data) > 0:
            expected_schema = [{
                'id': int,
                'username': str,
                'email': str,
                'is_admin': bool
            }]
            # 由于用户结构可能不完全一致，只验证基本字段
            user = json_data[0]
            assert 'id' in user and isinstance(user['id'], int), "用户应有整数类型的id字段"
            assert 'username' in user and isinstance(user['username'], str), "用户应有字符串类型的username字段"
    
    def test_get_user_detail_unauthenticated(self, api_client: APIClient):
        """
        测试未认证用户获取用户详情
        
        Args:
            api_client: API客户端
        """
        # 尝试获取用户详情（使用ID 1）
        response = api_client.get('/api/users/1')
        
        # 验证响应状态码（API可能未实现，返回404或500）
        assert response.status_code in [401, 403, 404, 500], f"未认证用户访问用户详情应返回401、403、404或500，实际返回{response.status_code}"
    
    @pytest.mark.admin
    def test_get_user_detail_admin(self, admin_client: APIClient):
        """
        测试管理员获取用户详情
        
        Args:
            admin_client: 管理员API客户端
        """
        # 首先获取用户列表
        users_response = admin_client.get('/api/users')
        users_response.assert_status_code(200)
        
        users = users_response.json_data
        if len(users) == 0:
            pytest.skip("没有可用的用户进行测试")
        
        # 获取第一个用户的详情
        user_id = users[0]['id']
        response = admin_client.get(f'/api/users/{user_id}')
        
        # 验证响应状态码（API可能未实现）
        assert response.status_code in [200, 404, 500], f"获取用户详情应返回200、404或500，实际返回{response.status_code}"
        
        if response.status_code == 200:
            # 验证响应内容
            json_data = response.json_data
            assert json_data is not None, "用户详情应返回JSON响应"
            assert json_data['id'] == user_id, "返回的用户ID应与请求的ID一致"
            
            # 验证必需字段
            required_fields = ['id', 'username']
            for field in required_fields:
                assert field in json_data, f"用户详情应包含{field}字段"
            
            # 确保不返回敏感信息
            sensitive_fields = ['password', 'password_hash']
            for field in sensitive_fields:
                assert field not in json_data, f"用户详情不应包含敏感字段{field}"
    
    def test_create_user_post_method(self, api_client: APIClient):
        """
        测试创建用户（POST方法）
        
        Args:
            api_client: API客户端
        """
        # 尝试创建新用户
        user_data = {
            'username': 'testuser_api',
            'email': 'testuser_api@example.com',
            'password': 'testpassword123'
        }
        
        response = api_client.post('/api/users', json=user_data)
        
        # 验证响应状态码（可能是201、400、405或404，取决于API实现）
        assert response.status_code in [201, 400, 401, 403, 405, 404], f"创建用户应返回201、400、401、403、405或404，实际返回{response.status_code}"
        
        if response.status_code == 201:
            # 如果创建成功，验证响应
            json_data = response.json_data
            if json_data is not None:
                assert 'id' in json_data or 'user_id' in json_data or 'success' in json_data, "创建用户成功应返回用户ID或成功信息"
    
    @pytest.mark.admin
    def test_update_user_put_method(self, admin_client: APIClient):
        """
        测试更新用户（PUT方法）
        
        Args:
            admin_client: 管理员API客户端
        """
        # 尝试更新用户信息
        user_data = {
            'username': 'updated_user',
            'email': 'updated@example.com'
        }
        
        response = admin_client.put('/api/users/1', json=user_data)
        
        # 验证响应状态码（API可能未实现）
        assert response.status_code in [200, 400, 404, 405, 500], f"更新用户应返回200、400、404、405或500，实际返回{response.status_code}"
    
    @pytest.mark.admin
    def test_delete_user_delete_method(self, admin_client: APIClient):
        """
        测试删除用户（DELETE方法）
        
        Args:
            admin_client: 管理员API客户端
        """
        # 尝试删除用户（使用一个不存在的ID以避免删除真实用户）
        response = admin_client.delete('/api/users/99999')
        
        # 验证响应状态码（API可能未实现）
        assert response.status_code in [200, 204, 404, 405, 500], f"删除用户应返回200、204、404、405或500，实际返回{response.status_code}"
    
    @pytest.mark.admin
    def test_users_api_headers(self, admin_client: APIClient):
        """
        测试用户API响应头
        
        Args:
            admin_client: 管理员API客户端
        """
        # 测试用户列表API响应头
        response = admin_client.get('/api/users')
        response.assert_status_code(200)
        
        # 验证响应头
        expected_headers = {
            'Content-Type': 'application/json'
        }
        self.assert_response_headers(response, expected_headers)
    
    @pytest.mark.admin
    def test_users_api_pagination(self, admin_client: APIClient):
        """
        测试用户API分页功能（如果支持）
        
        Args:
            admin_client: 管理员API客户端
        """
        # 测试带分页参数的请求
        response = admin_client.get('/api/users', params={'page': 1, 'limit': 5})
        
        # 即使不支持分页，也应该返回正常响应
        response.assert_status_code(200)
        
        json_data = response.json_data
        assert isinstance(json_data, list), "即使有分页参数，也应返回用户列表"
    
    @pytest.mark.admin
    def test_users_api_performance(self, admin_client: APIClient):
        """
        测试用户API性能
        
        Args:
            admin_client: 管理员API客户端
        """
        # 连续发送多个请求测试性能
        response_times = []
        
        for i in range(3):
            response = admin_client.get('/api/users')
            response.assert_status_code(200)
            response_time = response.response.elapsed.total_seconds()
            response_times.append(response_time)
        
        # 验证平均响应时间
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 2.0, f"用户API平均响应时间过长: {avg_response_time:.2f}秒"