# -*- coding: utf-8 -*-
"""
API测试客户端
提供统一的API请求接口和响应处理
"""

import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class APIClient:
    """API测试客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs):
        """
        发送GET请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            **kwargs: 其他请求参数
            
        Returns:
            APIResponse: 响应对象
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.get(url, params=params, **kwargs)
        return APIResponse(response)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None, **kwargs):
        """
        发送POST请求
        
        Args:
            endpoint: API端点
            data: 表单数据
            json_data: JSON数据
            **kwargs: 其他请求参数
            
        Returns:
            APIResponse: 响应对象
        """
        url = urljoin(self.base_url, endpoint)
        if json_data is not None:
            response = self.session.post(url, json=json_data, **kwargs)
        else:
            response = self.session.post(url, data=data, **kwargs)
        return APIResponse(response)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None, **kwargs):
        """
        发送PUT请求
        
        Args:
            endpoint: API端点
            data: 表单数据
            json_data: JSON数据
            **kwargs: 其他请求参数
            
        Returns:
            APIResponse: 响应对象
        """
        url = urljoin(self.base_url, endpoint)
        if json_data is not None:
            response = self.session.put(url, json=json_data, **kwargs)
        else:
            response = self.session.put(url, data=data, **kwargs)
        return APIResponse(response)
    
    def delete(self, endpoint: str, **kwargs):
        """
        发送DELETE请求
        
        Args:
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            APIResponse: 响应对象
        """
        url = urljoin(self.base_url, endpoint)
        response = self.session.delete(url, **kwargs)
        return APIResponse(response)
    
    def set_auth_token(self, token: str):
        """
        设置认证令牌
        
        Args:
            token: 认证令牌
        """
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def set_session_cookie(self, session_id: str):
        """
        设置会话Cookie
        
        Args:
            session_id: 会话ID
        """
        self.session.cookies.set('session', session_id)
    
    def login(self, username: str, password: str):
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            APIResponse: 登录响应
        """
        # 临时移除Content-Type头部并修改Accept头部以避免Flask清空session
        original_content_type = self.session.headers.pop('Content-Type', None)
        original_accept = None
        
        if 'Accept' in self.session.headers:
            original_accept = self.session.headers['Accept']
            self.session.headers['Accept'] = 'text/html'
            print(f"DEBUG: 修改Accept头部: {original_accept} -> text/html")
        
        print(f"DEBUG: 移除的Content-Type: {original_content_type}")
        print(f"DEBUG: 登录前头部: {dict(self.session.headers)}")
        
        try:
            url = urljoin(self.base_url, '/login')
            print(f"DEBUG: 请求URL: {url}")
            print(f"DEBUG: base_url: {self.base_url}")
            print(f"DEBUG: 请求数据: {{'username': '{username}', 'password': '***'}}")
            
            response = self.session.post(url, data={
                'username': username,
                'password': password
            }, allow_redirects=False)
            print(f"DEBUG: 登录响应状态码: {response.status_code}")
            print(f"DEBUG: 登录响应Set-Cookie: {response.headers.get('Set-Cookie', 'None')}")
            print(f"DEBUG: 登录后session cookies: {dict(self.session.cookies)}")
            print(f"DEBUG: 响应内容长度: {len(response.text)}")
            print(f"DEBUG: 响应Content-Type: {response.headers.get('Content-Type', 'None')}")
            
            # 检查是否是重定向响应
            if response.status_code == 302:
                print(f"DEBUG: 检测到重定向，Location: {response.headers.get('Location', 'None')}")
            elif response.status_code == 200:
                # 如果是200但内容是HTML，说明登录失败
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    print(f"DEBUG: 收到HTML响应，可能登录失败")
                    print(f"DEBUG: 响应内容前200字符: {response.text[:200]}")
            
            return APIResponse(response)
        finally:
            # 恢复Content-Type头部
            if original_content_type:
                self.session.headers['Content-Type'] = original_content_type
                print(f"DEBUG: 恢复Content-Type: {original_content_type}")
            
            # 恢复Accept头部
            if original_accept:
                self.session.headers['Accept'] = original_accept
                print(f"DEBUG: 恢复Accept头部: {original_accept}")
    
    def logout(self):
        """
        用户登出
        
        Returns:
            APIResponse: 登出响应
        """
        return self.post('/logout')
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class APIResponse:
    """API响应包装类"""
    
    def __init__(self, response: requests.Response):
        """
        初始化响应包装器
        
        Args:
            response: requests响应对象
        """
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.text = response.text
        
        try:
            self.json_data = response.json()
        except (json.JSONDecodeError, ValueError):
            self.json_data = None
    
    @property
    def is_success(self) -> bool:
        """
        检查响应是否成功
        
        Returns:
            bool: 是否成功（状态码2xx）
        """
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self) -> bool:
        """
        检查是否为客户端错误
        
        Returns:
            bool: 是否为客户端错误（状态码4xx）
        """
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """
        检查是否为服务器错误
        
        Returns:
            bool: 是否为服务器错误（状态码5xx）
        """
        return 500 <= self.status_code < 600
    
    def get_json_value(self, key: str, default: Any = None) -> Any:
        """
        获取JSON响应中的值
        
        Args:
            key: 键名
            default: 默认值
            
        Returns:
            Any: 对应的值
        """
        if self.json_data is None:
            return default
        return self.json_data.get(key, default)
    
    def assert_status_code(self, expected_code: int):
        """
        断言状态码
        
        Args:
            expected_code: 期望的状态码
            
        Raises:
            AssertionError: 状态码不匹配时抛出
        """
        assert self.status_code == expected_code, f"期望状态码 {expected_code}，实际状态码 {self.status_code}"
    
    def assert_json_contains(self, key: str, expected_value: Any = None):
        """
        断言JSON响应包含指定键
        
        Args:
            key: 键名
            expected_value: 期望的值（可选）
            
        Raises:
            AssertionError: 键不存在或值不匹配时抛出
        """
        assert self.json_data is not None, "响应不是有效的JSON格式"
        assert key in self.json_data, f"响应JSON中不包含键 '{key}'"
        
        if expected_value is not None:
            actual_value = self.json_data[key]
            assert actual_value == expected_value, f"键 '{key}' 的值不匹配，期望 {expected_value}，实际 {actual_value}"
    
    def assert_success(self):
        """
        断言响应成功
        
        Raises:
            AssertionError: 响应不成功时抛出
        """
        assert self.is_success, f"API请求失败，状态码: {self.status_code}，响应: {self.text}"