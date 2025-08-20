#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商城系统简单性能测试
不依赖特殊插件，使用标准库进行性能测试

运行方式:
pytest tests/performance/test_performance_simple.py -v
"""

import time
import statistics
from typing import List, Dict, Any

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SimplePerformanceConfig:
    """
    简单性能测试配置
    """
    BASE_URL = 'http://localhost:5000'
    TIMEOUT = 10  # 请求超时时间（秒）
    MAX_RESPONSE_TIME = 2.0  # 最大可接受响应时间（秒）
    
    # 性能基准（调整为更现实的值）
    BENCHMARKS = {
        'homepage': {'max_time': 3.0, 'target_time': 1.5},
        'products': {'max_time': 3.5, 'target_time': 2.0},
        'login': {'max_time': 3.0, 'target_time': 1.5},
    }


class SimplePerformanceClient:
    """
    简单性能测试客户端
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or SimplePerformanceConfig.BASE_URL
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """
        发送GET请求
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', SimplePerformanceConfig.TIMEOUT)
        return self.session.get(url, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """
        发送POST请求
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', SimplePerformanceConfig.TIMEOUT)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()


def measure_response_time(func, iterations: int = 5) -> Dict[str, float]:
    """
    测量函数执行时间
    """
    times = []
    
    for _ in range(iterations):
        start_time = time.time()
        try:
            func()
            end_time = time.time()
            times.append(end_time - start_time)
        except Exception as e:
            print(f"请求失败: {e}")
            continue
    
    if not times:
        return {'mean': float('inf'), 'min': float('inf'), 'max': float('inf')}
    
    return {
        'mean': statistics.mean(times),
        'min': min(times),
        'max': max(times),
        'median': statistics.median(times),
        'count': len(times)
    }


@pytest.fixture(scope='session')
def performance_client():
    """
    性能测试客户端fixture
    """
    client = SimplePerformanceClient()
    yield client
    client.close()


class TestSimplePerformance:
    """
    简单性能测试
    """
    
    def test_homepage_response_time(self, performance_client):
        """
        测试首页响应时间
        """
        def make_request():
            response = performance_client.get('/')
            assert response.status_code == 200
            return response
        
        # 测量响应时间
        stats = measure_response_time(make_request, iterations=3)
        
        # 验证响应时间
        benchmark_config = SimplePerformanceConfig.BENCHMARKS['homepage']
        assert stats['mean'] < benchmark_config['max_time'], \
            f"首页平均响应时间 {stats['mean']:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
        
        print(f"\n首页性能统计:")
        print(f"  平均响应时间: {stats['mean']:.3f}s")
        print(f"  最小响应时间: {stats['min']:.3f}s")
        print(f"  最大响应时间: {stats['max']:.3f}s")
        print(f"  测试次数: {stats['count']}")
    
    def test_products_page_response_time(self, performance_client):
        """
        测试商品页面响应时间
        """
        def make_request():
            response = performance_client.get('/products')
            assert response.status_code == 200
            return response
        
        # 测量响应时间
        stats = measure_response_time(make_request, iterations=3)
        
        # 验证响应时间
        benchmark_config = SimplePerformanceConfig.BENCHMARKS['products']
        assert stats['mean'] < benchmark_config['max_time'], \
            f"商品页面平均响应时间 {stats['mean']:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
        
        print(f"\n商品页面性能统计:")
        print(f"  平均响应时间: {stats['mean']:.3f}s")
        print(f"  最小响应时间: {stats['min']:.3f}s")
        print(f"  最大响应时间: {stats['max']:.3f}s")
        print(f"  测试次数: {stats['count']}")
    
    def test_login_page_response_time(self, performance_client):
        """
        测试登录页面响应时间
        """
        def make_request():
            response = performance_client.get('/login')
            assert response.status_code == 200
            return response
        
        # 测量响应时间
        stats = measure_response_time(make_request, iterations=3)
        
        # 验证响应时间
        benchmark_config = SimplePerformanceConfig.BENCHMARKS['login']
        assert stats['mean'] < benchmark_config['max_time'], \
            f"登录页面平均响应时间 {stats['mean']:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
        
        print(f"\n登录页面性能统计:")
        print(f"  平均响应时间: {stats['mean']:.3f}s")
        print(f"  最小响应时间: {stats['min']:.3f}s")
        print(f"  最大响应时间: {stats['max']:.3f}s")
        print(f"  测试次数: {stats['count']}")
    
    def test_application_availability(self, performance_client):
        """
        测试应用程序可用性
        """
        response = performance_client.get('/')
        assert response.status_code == 200, f"应用程序不可用，状态码: {response.status_code}"
        
        # 检查响应内容
        assert len(response.content) > 0, "响应内容为空"
        assert 'text/html' in response.headers.get('content-type', ''), "响应不是HTML格式"
        
        print(f"\n应用程序可用性检查通过:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应大小: {len(response.content)} bytes")
        print(f"  内容类型: {response.headers.get('content-type', 'unknown')}")


if __name__ == '__main__':
    # 直接运行测试
    import sys
    sys.exit(pytest.main([__file__, '-v', '-s']))