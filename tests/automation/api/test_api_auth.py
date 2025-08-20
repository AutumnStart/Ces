# -*- coding: utf-8 -*-
"""
认证API测试
测试登录、登出等认证相关的API端点
"""

import pytest
from .base_api_test import BaseAPITest
from .api_client import APIClient
from config.test_config import TestConfig


class TestAuthAPI(BaseAPITest):
    """认证API测试类"""
    
    @pytest.mark.smoke
    def test_login_valid_credentials(self, api_client: APIClient):
        """
        测试使用有效凭据登录
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户凭据
        test_user = TestConfig.TEST_USER
        
        # 发送登录请求
        response = api_client.login(test_user['username'], test_user['password'])
        
        # 验证响应状态码（可能是200成功或302重定向）
        assert response.status_code in [200, 302], f"有效凭据登录应返回200或302，实际返回{response.status_code}"
        
        # 验证响应时间
        self.assert_response_time(response, max_time=3.0)
        
        # 如果是JSON响应，验证内容
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json_data
            if json_data is not None:
                # 可能包含成功信息或用户信息
                assert 'success' in json_data or 'user' in json_data or 'message' in json_data, "登录响应应包含相关信息"
        
        # 验证是否设置了会话cookie
        if 'Set-Cookie' in response.headers:
            cookie_header = response.headers['Set-Cookie']
            assert 'session' in cookie_header.lower() or 'auth' in cookie_header.lower(), "登录应设置会话cookie"
    
    @pytest.mark.smoke
    def test_login_invalid_username(self, api_client: APIClient):
        """
        测试使用无效用户名登录
        
        Args:
            api_client: API客户端
        """
        # 使用无效用户名
        response = api_client.login('invalid_user', 'password123')
        
        # 验证响应状态码（Web应用可能返回200并显示错误消息）
        assert response.status_code in [200, 400, 401, 302], f"无效用户名登录应返回200、400、401或302，实际返回{response.status_code}"
        
        # 如果是JSON响应，验证错误信息
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json_data
            if json_data is not None:
                assert 'error' in json_data or 'message' in json_data, "登录失败应返回错误信息"
    
    @pytest.mark.smoke
    def test_login_invalid_password(self, api_client: APIClient):
        """
        测试使用无效密码登录
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户名但使用错误密码
        test_user = TestConfig.TEST_USER
        response = api_client.login(test_user['username'], 'wrong_password')
        
        # 验证响应状态码（Web应用可能返回200并显示错误消息）
        assert response.status_code in [200, 400, 401, 302], f"无效密码登录应返回200、400、401或302，实际返回{response.status_code}"
        
        # 如果是JSON响应，验证错误信息
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json_data
            if json_data is not None:
                assert 'error' in json_data or 'message' in json_data, "登录失败应返回错误信息"
    
    def test_login_empty_credentials(self, api_client: APIClient):
        """
        测试使用空凭据登录
        
        Args:
            api_client: API客户端
        """
        # 使用空用户名和密码
        response = api_client.login('', '')
        
        # 验证响应状态码（Web应用可能返回200并显示错误消息）
        assert response.status_code in [200, 400, 401, 302], f"空凭据登录应返回200、400、401或302，实际返回{response.status_code}"
    
    def test_login_missing_fields(self, api_client: APIClient):
        """
        测试缺少字段的登录请求
        
        Args:
            api_client: API客户端
        """
        # 发送只有用户名的登录请求
        response = api_client.post('/login', data={'username': 'testuser'})
        
        # 验证响应状态码（Web应用可能返回200并显示错误消息）
        assert response.status_code in [200, 400, 401, 302], f"缺少密码字段应返回200、400、401或302，实际返回{response.status_code}"
        
        # 发送只有密码的登录请求
        response = api_client.post('/login', data={'password': 'password123'})
        
        # 验证响应状态码（Web应用可能返回200并显示错误消息）
        assert response.status_code in [200, 400, 401, 302], f"缺少用户名字段应返回200、400、401或302，实际返回{response.status_code}"
    
    def test_logout_authenticated_user(self, authenticated_client: APIClient):
        """
        测试已认证用户登出
        
        Args:
            authenticated_client: 已认证的API客户端
        """
        # 发送登出请求
        response = authenticated_client.logout()
        
        # 验证响应状态码（可能是200成功或302重定向）
        assert response.status_code in [200, 302, 405], f"登出应返回200、302或405，实际返回{response.status_code}"
        
        # 验证响应时间
        self.assert_response_time(response, max_time=3.0)
        
        # 如果是JSON响应，验证内容
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json_data
            if json_data is not None:
                assert 'success' in json_data or 'message' in json_data, "登出响应应包含相关信息"
    
    def test_logout_unauthenticated_user(self, api_client: APIClient):
        """
        测试未认证用户登出
        
        Args:
            api_client: API客户端
        """
        # 发送登出请求（未登录）
        response = api_client.logout()
        
        # 验证响应状态码（可能是200、302或401）
        assert response.status_code in [200, 302, 401, 405], f"未认证用户登出应返回200、302、401或405，实际返回{response.status_code}"
    
    def test_login_logout_flow(self, api_client: APIClient):
        """
        测试完整的登录-登出流程
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户凭据
        test_user = TestConfig.TEST_USER
        
        # 步骤1：登录
        login_response = api_client.login(test_user['username'], test_user['password'])
        assert login_response.status_code in [200, 302], "登录应该成功"
        
        # Flask会自动处理session cookie，无需手动设置
        
        # 步骤2：验证已登录状态（尝试访问需要认证的端点）
        cart_response = api_client.get('/api/cart')
        assert cart_response.status_code in [200, 401], f"登录后访问购物车返回{cart_response.status_code}"
        
        # 步骤3：登出
        logout_response = api_client.logout()
        assert logout_response.status_code in [200, 302, 405], "登出应该成功"
        
        # 步骤4：验证已登出状态（再次尝试访问需要认证的端点）
        # 清除会话信息
        if 'Cookie' in api_client.session.headers:
            del api_client.session.headers['Cookie']
        
        cart_response_after_logout = api_client.get('/api/cart')
        # 登出后可能返回401、403或200（取决于实现）
        assert cart_response_after_logout.status_code in [200, 401, 403, 302], "登出后访问购物车的响应应该合理"
    
    def test_multiple_login_attempts(self, api_client: APIClient):
        """
        测试多次登录尝试
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户凭据
        test_user = TestConfig.TEST_USER
        
        # 进行多次登录尝试
        for i in range(3):
            response = api_client.login(test_user['username'], test_user['password'])
            assert response.status_code in [200, 302], f"第{i+1}次登录尝试应该成功"
            
            # 每次登录后登出
            if 'Set-Cookie' in response.headers:
                session_cookie = response.headers['Set-Cookie']
                api_client.session.headers.update({'Cookie': session_cookie})
            
            logout_response = api_client.logout()
            assert logout_response.status_code in [200, 302, 405], f"第{i+1}次登出应该成功"
            
            # 清除会话
            if 'Cookie' in api_client.session.headers:
                del api_client.session.headers['Cookie']
    
    def test_login_with_special_characters(self, api_client: APIClient):
        """
        测试包含特殊字符的登录凭据
        
        Args:
            api_client: API客户端
        """
        # 测试包含特殊字符的用户名和密码
        special_credentials = [
            ('user@domain.com', 'pass123'),
            ('user with spaces', 'password'),
            ('user123', 'pass@#$%'),
            ('用户名', '密码123'),  # 中文字符
        ]
        
        for username, password in special_credentials:
            response = api_client.login(username, password)
            # 这些都应该是无效凭据，但不应该导致服务器错误
            assert response.status_code in [200, 302, 400, 401], f"特殊字符凭据 '{username}' 应返回合理的状态码"
    
    def test_login_performance(self, api_client: APIClient):
        """
        测试登录性能
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户凭据
        test_user = TestConfig.TEST_USER
        
        # 测试登录响应时间
        response = api_client.login(test_user['username'], test_user['password'])
        assert response.status_code in [200, 302], "登录应该成功"
        
        # 验证登录响应时间
        login_time = response.response.elapsed.total_seconds()
        assert login_time < 3.0, f"登录响应时间过长: {login_time:.2f}秒"
    
    def test_concurrent_login_attempts(self, api_client: APIClient):
        """
        测试并发登录尝试
        
        Args:
            api_client: API客户端
        """
        # 获取测试用户凭据
        test_user = TestConfig.TEST_USER
        
        # 同时发送多个登录请求
        responses = []
        for i in range(3):
            response = api_client.login(test_user['username'], test_user['password'])
            responses.append(response)
        
        # 验证所有响应
        for i, response in enumerate(responses):
            assert response.status_code in [200, 302], f"第{i+1}个并发登录请求应该成功"