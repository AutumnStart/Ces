#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试运行脚本
提供便捷的性能测试执行和报告生成功能

使用方式:
python run_performance_tests.py --help
python run_performance_tests.py --quick
python run_performance_tests.py --full
python run_performance_tests.py --stress
python run_performance_tests.py --locust
"""

import os
import sys
import time
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PerformanceTestRunner:
    """
    性能测试运行器
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.reports_dir = self.base_dir / 'reports'
        self.reports_dir.mkdir(exist_ok=True)
        
        # 确保应用程序正在运行
        self.app_url = 'http://localhost:5000'
        self.check_app_running()
    
    def check_app_running(self):
        """
        检查应用程序是否正在运行
        """
        try:
            import requests
            response = requests.get(self.app_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ 应用程序正在运行: {self.app_url}")
            else:
                print(f"⚠️ 应用程序响应异常: {response.status_code}")
        except Exception as e:
            print(f"❌ 无法连接到应用程序: {self.app_url}")
            print(f"错误: {e}")
            print("请确保应用程序正在运行，然后重新执行测试")
            print("启动命令: python app/app.py")
            sys.exit(1)
    
    def run_pytest_performance(self, test_type: str = 'basic') -> Dict[str, Any]:
        """
        运行pytest性能测试
        """
        print(f"\n🚀 开始运行 {test_type} 性能测试...")
        
        # 生成报告文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'pytest_performance_{test_type}_{timestamp}.json'
        html_report = self.reports_dir / f'pytest_performance_{test_type}_{timestamp}.html'
        
        # 构建pytest命令
        cmd = [
            'python', '-m', 'pytest',
            str(self.base_dir / 'test_performance.py'),
            '-v',
            '--tb=short'
        ]
        
        # 尝试添加HTML报告（如果插件可用）
        try:
            import pytest_html
            cmd.extend([f'--html={html_report}', '--self-contained-html'])
        except ImportError:
            print("⚠️ pytest-html 插件未安装，跳过HTML报告生成")
        
        # 尝试添加JSON报告（如果插件可用）
        try:
            import pytest_json_report
            cmd.append(f'--json-report={report_file}')
        except ImportError:
            print("⚠️ pytest-json-report 插件未安装，跳过JSON报告生成")
        
        # 根据测试类型添加特定参数
        if test_type == 'quick':
            cmd.extend(['-k', 'test_homepage_response_time or test_products_page_response_time'])
        elif test_type == 'benchmark':
            cmd.extend(['--benchmark-only', '--benchmark-json=' + str(report_file.with_suffix('.benchmark.json'))])
        elif test_type == 'concurrent':
            cmd.extend(['-k', 'concurrent', '-n', '4'])
        elif test_type == 'stress':
            cmd.extend(['-k', 'stress'])
        elif test_type == 'memory':
            cmd.extend(['-k', 'memory'])
        
        # 执行测试
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            execution_time = time.time() - start_time
            
            print(f"\n📊 测试执行完成，耗时: {execution_time:.2f}秒")
            print(f"📄 报告文件: {html_report}")
            
            if result.returncode == 0:
                print("✅ 所有测试通过")
            else:
                print("❌ 部分测试失败")
                print("错误输出:")
                print(result.stderr)
            
            return {
                'type': f'pytest_{test_type}',
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'report_file': str(html_report),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            return {
                'type': f'pytest_{test_type}',
                'success': False,
                'error': str(e)
            }
    
    def run_locust_test(self, users: int = 10, spawn_rate: int = 2, duration: str = '60s') -> Dict[str, Any]:
        """
        运行Locust负载测试
        """
        print(f"\n🐝 开始运行 Locust 负载测试...")
        print(f"用户数: {users}, 生成速率: {spawn_rate}/s, 持续时间: {duration}")
        
        # 生成报告文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_prefix = self.reports_dir / f'locust_{timestamp}'
        html_report = self.reports_dir / f'locust_report_{timestamp}.html'
        
        # 构建Locust命令
        cmd = [
            'python', '-m', 'locust',
            '-f', str(self.base_dir / 'locustfile.py'),
            '--host', self.app_url,
            '--users', str(users),
            '--spawn-rate', str(spawn_rate),
            '--run-time', duration,
            '--headless',
            '--csv', str(csv_prefix),
            '--html', str(html_report)
        ]
        
        # 执行测试
        start_time = time.time()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            execution_time = time.time() - start_time
            
            print(f"\n📊 Locust测试执行完成，耗时: {execution_time:.2f}秒")
            print(f"📄 HTML报告: {html_report}")
            print(f"📄 CSV数据: {csv_prefix}_stats.csv")
            
            if result.returncode == 0:
                print("✅ Locust测试完成")
            else:
                print("❌ Locust测试出现问题")
                print("错误输出:")
                print(result.stderr)
            
            return {
                'type': 'locust',
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'html_report': str(html_report),
                'csv_prefix': str(csv_prefix),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            print(f"❌ Locust测试执行失败: {e}")
            return {
                'type': 'locust',
                'success': False,
                'error': str(e)
            }
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """
        生成汇总报告
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = self.reports_dir / f'performance_summary_{timestamp}.json'
        
        summary = {
            'timestamp': timestamp,
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r.get('success', False)),
            'failed_tests': sum(1 for r in results if not r.get('success', False)),
            'total_execution_time': sum(r.get('execution_time', 0) for r in results),
            'results': results
        }
        
        # 保存汇总报告
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 打印汇总信息
        print(f"\n📋 性能测试汇总报告")
        print(f"{'='*50}")
        print(f"测试时间: {timestamp}")
        print(f"总测试数: {summary['total_tests']}")
        print(f"成功测试: {summary['successful_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"总执行时间: {summary['total_execution_time']:.2f}秒")
        print(f"汇总报告: {summary_file}")
        
        # 列出所有报告文件
        print(f"\n📁 生成的报告文件:")
        for result in results:
            if 'report_file' in result:
                print(f"  - {result['type']}: {result['report_file']}")
            if 'html_report' in result:
                print(f"  - {result['type']}: {result['html_report']}")
    
    def install_dependencies(self):
        """
        安装性能测试依赖
        """
        print("📦 安装性能测试依赖...")
        
        dependencies = [
            'pytest',
            'pytest-benchmark',
            'pytest-xdist',
            'pytest-html',
            'pytest-json-report',
            'locust',
            'requests'
        ]
        
        for dep in dependencies:
            try:
                subprocess.run(['pip', 'install', dep], check=True, capture_output=True)
                print(f"✅ {dep} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {dep} 安装失败: {e}")
    
    def run_quick_test(self):
        """
        运行快速性能测试
        """
        print("🏃‍♂️ 运行快速性能测试...")
        results = []
        results.append(self.run_pytest_performance('quick'))
        self.generate_summary_report(results)
    
    def run_full_test(self):
        """
        运行完整性能测试
        """
        print("🏃‍♂️ 运行完整性能测试...")
        results = []
        
        # 基础性能测试
        results.append(self.run_pytest_performance('basic'))
        
        # 基准测试
        results.append(self.run_pytest_performance('benchmark'))
        
        # 并发测试
        results.append(self.run_pytest_performance('concurrent'))
        
        # 内存泄漏检测
        results.append(self.run_pytest_performance('memory'))
        
        self.generate_summary_report(results)
    
    def run_stress_test(self):
        """
        运行压力测试
        """
        print("💪 运行压力测试...")
        results = []
        
        # pytest压力测试
        results.append(self.run_pytest_performance('stress'))
        
        # Locust负载测试
        results.append(self.run_locust_test(users=20, spawn_rate=5, duration='120s'))
        
        self.generate_summary_report(results)
    
    def run_locust_only(self, users: int = 10, duration: str = '60s'):
        """
        仅运行Locust测试
        """
        print("🐝 运行Locust负载测试...")
        results = []
        results.append(self.run_locust_test(users=users, duration=duration))
        self.generate_summary_report(results)


def main():
    parser = argparse.ArgumentParser(description='商城系统性能测试运行器')
    parser.add_argument('--quick', action='store_true', help='运行快速性能测试')
    parser.add_argument('--full', action='store_true', help='运行完整性能测试')
    parser.add_argument('--stress', action='store_true', help='运行压力测试')
    parser.add_argument('--locust', action='store_true', help='仅运行Locust负载测试')
    parser.add_argument('--install-deps', action='store_true', help='安装测试依赖')
    parser.add_argument('--users', type=int, default=10, help='Locust测试用户数 (默认: 10)')
    parser.add_argument('--duration', default='60s', help='Locust测试持续时间 (默认: 60s)')
    
    args = parser.parse_args()
    
    runner = PerformanceTestRunner()
    
    if args.install_deps:
        runner.install_dependencies()
        return
    
    if args.quick:
        runner.run_quick_test()
    elif args.full:
        runner.run_full_test()
    elif args.stress:
        runner.run_stress_test()
    elif args.locust:
        runner.run_locust_only(users=args.users, duration=args.duration)
    else:
        print("请选择一个测试选项:")
        print("  --quick     快速性能测试")
        print("  --full      完整性能测试")
        print("  --stress    压力测试")
        print("  --locust    Locust负载测试")
        print("  --install-deps  安装测试依赖")
        print("\n示例:")
        print("  python run_performance_tests.py --quick")
        print("  python run_performance_tests.py --locust --users 20 --duration 120s")


if __name__ == '__main__':
    main()