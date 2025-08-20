#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商城系统性能测试
使用 pytest 和 requests 进行性能测试

安装依赖:
pip install pytest requests pytest-benchmark pytest-xdist

运行方式:
pytest tests/performance/test_performance.py -v
pytest tests/performance/test_performance.py -v --benchmark-only
pytest tests/performance/test_performance.py -v -n 4  # 并发测试
"""

import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PerformanceTestConfig:
    """
    性能测试配置
    """
    BASE_URL = 'http://localhost:5000'
    TIMEOUT = 10  # 请求超时时间（秒）
    MAX_RESPONSE_TIME = 2.0  # 最大可接受响应时间（秒）
    CONCURRENT_USERS = 10  # 并发用户数
    REQUESTS_PER_USER = 5  # 每个用户的请求数
    
    # 性能基准
    BENCHMARKS = {
        'homepage': {'max_time': 1.0, 'target_time': 0.5},
        'products': {'max_time': 2.0, 'target_time': 1.0},
        'product_detail': {'max_time': 1.5, 'target_time': 0.8},
        'login': {'max_time': 2.0, 'target_time': 1.0},
        'search': {'max_time': 3.0, 'target_time': 1.5},
    }


class PerformanceTestClient:
    """
    性能测试客户端
    """
    
    def __init__(self, base_url: str = PerformanceTestConfig.BASE_URL):
        self.base_url = base_url
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        创建配置了重试策略的会话
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """
        发送GET请求
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, timeout=PerformanceTestConfig.TIMEOUT, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """
        发送POST请求
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, timeout=PerformanceTestConfig.TIMEOUT, **kwargs)
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()


class PerformanceMetrics:
    """
    性能指标收集器
    """
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def add_metric(self, endpoint: str, response_time: float, status_code: int, success: bool):
        """
        添加性能指标
        """
        self.metrics.append({
            'endpoint': endpoint,
            'response_time': response_time,
            'status_code': status_code,
            'success': success,
            'timestamp': time.time()
        })
    
    def get_statistics(self, endpoint: str = None) -> Dict[str, Any]:
        """
        获取统计信息
        """
        if endpoint:
            filtered_metrics = [m for m in self.metrics if m['endpoint'] == endpoint]
        else:
            filtered_metrics = self.metrics
        
        if not filtered_metrics:
            return {}
        
        response_times = [m['response_time'] for m in filtered_metrics]
        success_count = sum(1 for m in filtered_metrics if m['success'])
        
        return {
            'total_requests': len(filtered_metrics),
            'success_requests': success_count,
            'success_rate': success_count / len(filtered_metrics) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99),
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        计算百分位数
        """
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture(scope='session')
def performance_client():
    """
    性能测试客户端fixture
    """
    client = PerformanceTestClient()
    yield client
    client.close()


@pytest.fixture(scope='session')
def metrics_collector():
    """
    性能指标收集器fixture
    """
    return PerformanceMetrics()


class TestBasicPerformance:
    """
    基础性能测试
    """
    
    def test_homepage_response_time(self, performance_client, benchmark):
        """
        测试首页响应时间
        """
        def make_request():
            response = performance_client.get('/')
            assert response.status_code == 200
            return response
        
        # 使用pytest-benchmark进行基准测试
        result = benchmark(make_request)
        
        # 验证响应时间
        benchmark_config = PerformanceTestConfig.BENCHMARKS['homepage']
        assert benchmark.stats.mean < benchmark_config['max_time'], \
            f"首页平均响应时间 {benchmark.stats.mean:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
    
    def test_products_page_response_time(self, performance_client, benchmark):
        """
        测试商品页面响应时间
        """
        def make_request():
            response = performance_client.get('/products')
            assert response.status_code == 200
            return response
        
        result = benchmark(make_request)
        
        benchmark_config = PerformanceTestConfig.BENCHMARKS['products']
        assert benchmark.stats.mean < benchmark_config['max_time'], \
            f"商品页面平均响应时间 {benchmark.stats.mean:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
    
    def test_product_detail_response_time(self, performance_client, benchmark):
        """
        测试商品详情页面响应时间
        """
        def make_request():
            # 测试商品ID 1的详情页面
            response = performance_client.get('/products/1')
            # 允许404状态码，因为商品可能不存在
            assert response.status_code in [200, 404]
            return response
        
        result = benchmark(make_request)
        
        benchmark_config = PerformanceTestConfig.BENCHMARKS['product_detail']
        assert benchmark.stats.mean < benchmark_config['max_time'], \
            f"商品详情页面平均响应时间 {benchmark.stats.mean:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
    
    def test_login_page_response_time(self, performance_client, benchmark):
        """
        测试登录页面响应时间
        """
        def make_request():
            response = performance_client.get('/login')
            assert response.status_code == 200
            return response
        
        result = benchmark(make_request)
        
        benchmark_config = PerformanceTestConfig.BENCHMARKS['login']
        assert benchmark.stats.mean < benchmark_config['max_time'], \
            f"登录页面平均响应时间 {benchmark.stats.mean:.3f}s 超过最大限制 {benchmark_config['max_time']}s"
    
    def test_search_response_time(self, performance_client, benchmark):
        """
        测试搜索功能响应时间
        """
        def make_request():
            response = performance_client.get('/products?search=test')
            assert response.status_code == 200
            return response
        
        result = benchmark(make_request)
        
        benchmark_config = PerformanceTestConfig.BENCHMARKS['search']
        assert benchmark.stats.mean < benchmark_config['max_time'], \
            f"搜索功能平均响应时间 {benchmark.stats.mean:.3f}s 超过最大限制 {benchmark_config['max_time']}s"


class TestConcurrentPerformance:
    """
    并发性能测试
    """
    
    def test_concurrent_homepage_access(self, metrics_collector):
        """
        测试首页并发访问
        """
        def make_concurrent_request(user_id: int) -> Dict[str, Any]:
            client = PerformanceTestClient()
            results = []
            
            try:
                for i in range(PerformanceTestConfig.REQUESTS_PER_USER):
                    start_time = time.time()
                    try:
                        response = client.get('/')
                        response_time = time.time() - start_time
                        success = response.status_code == 200
                        
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': response.status_code,
                            'success': success
                        })
                        
                        metrics_collector.add_metric('/', response_time, response.status_code, success)
                        
                    except Exception as e:
                        response_time = time.time() - start_time
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': 0,
                            'success': False,
                            'error': str(e)
                        })
                        
                        metrics_collector.add_metric('/', response_time, 0, False)
                        
            finally:
                client.close()
            
            return results
        
        # 执行并发测试
        with ThreadPoolExecutor(max_workers=PerformanceTestConfig.CONCURRENT_USERS) as executor:
            futures = [
                executor.submit(make_concurrent_request, user_id)
                for user_id in range(PerformanceTestConfig.CONCURRENT_USERS)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # 分析结果
        stats = metrics_collector.get_statistics('/')
        
        print(f"\n并发测试结果:")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求数: {stats['success_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"最大响应时间: {stats['max_response_time']:.3f}s")
        print(f"P95响应时间: {stats['p95_response_time']:.3f}s")
        print(f"P99响应时间: {stats['p99_response_time']:.3f}s")
        
        # 断言
        assert stats['success_rate'] >= 95, f"成功率 {stats['success_rate']:.2f}% 低于95%"
        assert stats['avg_response_time'] < 3.0, f"平均响应时间 {stats['avg_response_time']:.3f}s 超过3秒"
        assert stats['p95_response_time'] < 5.0, f"P95响应时间 {stats['p95_response_time']:.3f}s 超过5秒"
    
    def test_concurrent_products_access(self, metrics_collector):
        """
        测试商品页面并发访问
        """
        def make_concurrent_request(user_id: int) -> List[Dict[str, Any]]:
            client = PerformanceTestClient()
            results = []
            
            try:
                for i in range(PerformanceTestConfig.REQUESTS_PER_USER):
                    start_time = time.time()
                    try:
                        response = client.get('/products')
                        response_time = time.time() - start_time
                        success = response.status_code == 200
                        
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': response.status_code,
                            'success': success
                        })
                        
                        metrics_collector.add_metric('/products', response_time, response.status_code, success)
                        
                    except Exception as e:
                        response_time = time.time() - start_time
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': 0,
                            'success': False,
                            'error': str(e)
                        })
                        
                        metrics_collector.add_metric('/products', response_time, 0, False)
                        
            finally:
                client.close()
            
            return results
        
        # 执行并发测试
        with ThreadPoolExecutor(max_workers=PerformanceTestConfig.CONCURRENT_USERS) as executor:
            futures = [
                executor.submit(make_concurrent_request, user_id)
                for user_id in range(PerformanceTestConfig.CONCURRENT_USERS)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # 分析结果
        stats = metrics_collector.get_statistics('/products')
        
        print(f"\n商品页面并发测试结果:")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求数: {stats['success_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"最大响应时间: {stats['max_response_time']:.3f}s")
        print(f"P95响应时间: {stats['p95_response_time']:.3f}s")
        
        # 断言
        assert stats['success_rate'] >= 90, f"成功率 {stats['success_rate']:.2f}% 低于90%"
        assert stats['avg_response_time'] < 4.0, f"平均响应时间 {stats['avg_response_time']:.3f}s 超过4秒"


class TestStressTest:
    """
    压力测试
    """
    
    def test_stress_test_homepage(self, metrics_collector):
        """
        首页压力测试
        """
        stress_users = 20  # 压力测试用户数
        requests_per_user = 10  # 每个用户的请求数
        
        def stress_request(user_id: int) -> List[Dict[str, Any]]:
            client = PerformanceTestClient()
            results = []
            
            try:
                for i in range(requests_per_user):
                    start_time = time.time()
                    try:
                        response = client.get('/')
                        response_time = time.time() - start_time
                        success = response.status_code == 200
                        
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': response.status_code,
                            'success': success
                        })
                        
                        metrics_collector.add_metric('stress_/', response_time, response.status_code, success)
                        
                        # 压力测试中减少等待时间
                        time.sleep(0.1)
                        
                    except Exception as e:
                        response_time = time.time() - start_time
                        results.append({
                            'user_id': user_id,
                            'request_id': i,
                            'response_time': response_time,
                            'status_code': 0,
                            'success': False,
                            'error': str(e)
                        })
                        
                        metrics_collector.add_metric('stress_/', response_time, 0, False)
                        
            finally:
                client.close()
            
            return results
        
        # 执行压力测试
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=stress_users) as executor:
            futures = [
                executor.submit(stress_request, user_id)
                for user_id in range(stress_users)
            ]
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        total_time = time.time() - start_time
        
        # 分析结果
        stats = metrics_collector.get_statistics('stress_/')
        
        print(f"\n压力测试结果:")
        print(f"测试用户数: {stress_users}")
        print(f"每用户请求数: {requests_per_user}")
        print(f"总测试时间: {total_time:.2f}s")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求数: {stats['success_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"最大响应时间: {stats['max_response_time']:.3f}s")
        print(f"吞吐量: {stats['total_requests'] / total_time:.2f} 请求/秒")
        
        # 压力测试的断言相对宽松
        assert stats['success_rate'] >= 80, f"压力测试成功率 {stats['success_rate']:.2f}% 低于80%"
        assert stats['avg_response_time'] < 10.0, f"压力测试平均响应时间 {stats['avg_response_time']:.3f}s 超过10秒"


class TestMemoryLeakDetection:
    """
    内存泄漏检测测试
    """
    
    def test_memory_leak_detection(self, performance_client):
        """
        检测潜在的内存泄漏
        通过长时间运行相同请求来检测响应时间是否持续增长
        """
        response_times = []
        iterations = 50
        
        for i in range(iterations):
            start_time = time.time()
            response = performance_client.get('/')
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
            
            # 每10次请求检查一次趋势
            if (i + 1) % 10 == 0:
                recent_avg = statistics.mean(response_times[-10:])
                overall_avg = statistics.mean(response_times)
                
                print(f"迭代 {i+1}: 最近10次平均响应时间 {recent_avg:.3f}s, 总体平均 {overall_avg:.3f}s")
                
                # 如果最近的响应时间显著高于总体平均值，可能存在内存泄漏
                if recent_avg > overall_avg * 1.5 and i > 20:
                    pytest.fail(f"检测到可能的内存泄漏: 最近响应时间 {recent_avg:.3f}s 显著高于总体平均 {overall_avg:.3f}s")
            
            time.sleep(0.1)  # 短暂延迟
        
        # 最终检查
        first_quarter = statistics.mean(response_times[:iterations//4])
        last_quarter = statistics.mean(response_times[-iterations//4:])
        
        print(f"\n内存泄漏检测结果:")
        print(f"前1/4响应时间平均: {first_quarter:.3f}s")
        print(f"后1/4响应时间平均: {last_quarter:.3f}s")
        print(f"性能退化比例: {(last_quarter / first_quarter - 1) * 100:.2f}%")
        
        # 如果后期响应时间比前期高出50%以上，可能存在内存泄漏
        assert last_quarter < first_quarter * 1.5, \
            f"检测到性能退化: 后期响应时间 {last_quarter:.3f}s 比前期 {first_quarter:.3f}s 高出 {(last_quarter / first_quarter - 1) * 100:.2f}%"


if __name__ == '__main__':
    # 可以在这里添加一些配置或测试代码
    print("性能测试模块已准备就绪")
    print("运行命令:")
    print("  pytest tests/performance/test_performance.py -v")
    print("  pytest tests/performance/test_performance.py -v --benchmark-only")
    print("  pytest tests/performance/test_performance.py -v -n 4")