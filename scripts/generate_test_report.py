#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器
汇总所有测试结果并生成综合报告

使用方法:
python scripts/generate_test_report.py
python scripts/generate_test_report.py --output reports/summary.html
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import xml.etree.ElementTree as ET


class TestReportGenerator:
    """
    测试报告生成器
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.reports_dir = self.base_dir / 'reports'
        self.test_results = {
            'unit_tests': {},
            'api_tests': {},
            'ui_tests': {},
            'performance_tests': {},
            'security_tests': {}
        }
    
    def collect_test_results(self):
        """
        收集所有测试结果
        """
        print("📊 收集测试结果...")
        
        # 收集单元测试结果
        self._collect_pytest_results('unit_tests', 'tests/automation/api')
        
        # 收集API测试结果
        self._collect_pytest_results('api_tests', 'tests/automation/api')
        
        # 收集UI测试结果
        self._collect_pytest_results('ui_tests', 'tests/ui')
        
        # 收集性能测试结果
        self._collect_performance_results()
        
        # 收集安全测试结果
        self._collect_security_results()
    
    def _collect_pytest_results(self, test_type: str, test_dir: str):
        """
        收集pytest测试结果
        """
        # 查找JUnit XML报告
        junit_files = list(self.reports_dir.glob(f'*{test_type}*.xml'))
        if not junit_files:
            junit_files = list(Path(test_dir).glob('**/junit*.xml'))
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        errors = []
        
        for junit_file in junit_files:
            try:
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                # 解析测试套件
                for testsuite in root.findall('.//testsuite'):
                    total_tests += int(testsuite.get('tests', 0))
                    passed_tests += int(testsuite.get('tests', 0)) - int(testsuite.get('failures', 0)) - int(testsuite.get('errors', 0)) - int(testsuite.get('skipped', 0))
                    failed_tests += int(testsuite.get('failures', 0))
                    skipped_tests += int(testsuite.get('skipped', 0))
                    
                    # 收集错误信息
                    for testcase in testsuite.findall('.//testcase'):
                        failure = testcase.find('failure')
                        error = testcase.find('error')
                        if failure is not None:
                            errors.append({
                                'test': testcase.get('name'),
                                'type': 'failure',
                                'message': failure.get('message', ''),
                                'details': failure.text or ''
                            })
                        elif error is not None:
                            errors.append({
                                'test': testcase.get('name'),
                                'type': 'error',
                                'message': error.get('message', ''),
                                'details': error.text or ''
                            })
            except Exception as e:
                print(f"⚠️ 解析 {junit_file} 失败: {e}")
        
        self.test_results[test_type] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'errors': errors
        }
    
    def _collect_performance_results(self):
        """
        收集性能测试结果
        """
        perf_dir = self.base_dir / 'tests' / 'performance' / 'reports'
        
        # 查找性能测试报告
        summary_files = list(perf_dir.glob('performance_summary_*.json'))
        
        if summary_files:
            latest_file = max(summary_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.test_results['performance_tests'] = data
            except Exception as e:
                print(f"⚠️ 解析性能测试报告失败: {e}")
                self.test_results['performance_tests'] = {'error': str(e)}
        else:
            self.test_results['performance_tests'] = {'message': '未找到性能测试报告'}
    
    def _collect_security_results(self):
        """
        收集安全测试结果
        """
        # 查找安全扫描报告
        bandit_files = list(self.reports_dir.glob('bandit-report.json'))
        safety_files = list(self.reports_dir.glob('safety-report.json'))
        
        security_results = {
            'bandit': {},
            'safety': {}
        }
        
        # 解析Bandit报告
        if bandit_files:
            try:
                with open(bandit_files[0], 'r', encoding='utf-8') as f:
                    bandit_data = json.load(f)
                    security_results['bandit'] = {
                        'total_issues': len(bandit_data.get('results', [])),
                        'high_severity': len([r for r in bandit_data.get('results', []) if r.get('issue_severity') == 'HIGH']),
                        'medium_severity': len([r for r in bandit_data.get('results', []) if r.get('issue_severity') == 'MEDIUM']),
                        'low_severity': len([r for r in bandit_data.get('results', []) if r.get('issue_severity') == 'LOW']),
                        'issues': bandit_data.get('results', [])
                    }
            except Exception as e:
                security_results['bandit'] = {'error': str(e)}
        
        # 解析Safety报告
        if safety_files:
            try:
                with open(safety_files[0], 'r', encoding='utf-8') as f:
                    safety_data = json.load(f)
                    security_results['safety'] = {
                        'vulnerabilities': len(safety_data),
                        'issues': safety_data
                    }
            except Exception as e:
                security_results['safety'] = {'error': str(e)}
        
        self.test_results['security_tests'] = security_results
    
    def generate_html_report(self, output_file: str = None):
        """
        生成HTML格式的测试报告
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.reports_dir / f'test_summary_{timestamp}.html'
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._generate_html_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTML报告已生成: {output_path}")
        return output_path
    
    def _generate_html_content(self) -> str:
        """
        生成HTML内容
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告汇总</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .summary-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .summary-card.success {{
            border-left-color: #28a745;
        }}
        .summary-card.warning {{
            border-left-color: #ffc107;
        }}
        .summary-card.danger {{
            border-left-color: #dc3545;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .summary-card.success .number {{
            color: #28a745;
        }}
        .summary-card.warning .number {{
            color: #ffc107;
        }}
        .summary-card.danger .number {{
            color: #dc3545;
        }}
        .details {{
            padding: 0 30px 30px 30px;
        }}
        .test-section {{
            margin-bottom: 30px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
        }}
        .test-section-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            font-weight: bold;
            color: #495057;
        }}
        .test-section-content {{
            padding: 20px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: #28a745;
            transition: width 0.3s ease;
        }}
        .error-list {{
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            border-radius: 4px;
            padding: 15px;
            margin-top: 10px;
        }}
        .error-item {{
            background: white;
            border-left: 3px solid #dc3545;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}
        .error-item:last-child {{
            margin-bottom: 0;
        }}
        .error-title {{
            font-weight: bold;
            color: #dc3545;
        }}
        .error-message {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 测试报告汇总</h1>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="summary">
"""
        
        # 计算总体统计
        total_tests = sum(result.get('total', 0) for result in self.test_results.values() if isinstance(result, dict) and 'total' in result)
        total_passed = sum(result.get('passed', 0) for result in self.test_results.values() if isinstance(result, dict) and 'passed' in result)
        total_failed = sum(result.get('failed', 0) for result in self.test_results.values() if isinstance(result, dict) and 'failed' in result)
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # 添加汇总卡片
        html += f"""
            <div class="summary-card {'success' if overall_success_rate >= 90 else 'warning' if overall_success_rate >= 70 else 'danger'}">
                <h3>总体成功率</h3>
                <div class="number">{overall_success_rate:.1f}%</div>
                <p>{total_passed}/{total_tests} 测试通过</p>
            </div>
            
            <div class="summary-card success">
                <h3>通过测试</h3>
                <div class="number">{total_passed}</div>
                <p>成功执行的测试</p>
            </div>
            
            <div class="summary-card danger">
                <h3>失败测试</h3>
                <div class="number">{total_failed}</div>
                <p>需要修复的测试</p>
            </div>
            
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="number">{total_tests}</div>
                <p>执行的测试总数</p>
            </div>
        </div>
        
        <div class="details">
"""
        
        # 添加各类测试的详细信息
        test_types = {
            'unit_tests': '单元测试',
            'api_tests': 'API测试',
            'ui_tests': 'UI测试',
            'performance_tests': '性能测试',
            'security_tests': '安全测试'
        }
        
        for test_type, test_name in test_types.items():
            result = self.test_results.get(test_type, {})
            html += self._generate_test_section_html(test_name, result)
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_test_section_html(self, test_name: str, result: Dict[str, Any]) -> str:
        """
        生成测试部分的HTML
        """
        if not result or 'error' in result:
            return f"""
            <div class="test-section">
                <div class="test-section-header">{test_name}</div>
                <div class="test-section-content">
                    <p>❌ 未找到测试结果或解析失败</p>
                    {f'<p>错误: {result.get("error", "未知错误")}</p>' if 'error' in result else ''}
                </div>
            </div>
"""
        
        if 'total' in result:
            # 标准测试结果
            total = result.get('total', 0)
            passed = result.get('passed', 0)
            failed = result.get('failed', 0)
            success_rate = result.get('success_rate', 0)
            errors = result.get('errors', [])
            
            html = f"""
            <div class="test-section">
                <div class="test-section-header">{test_name}</div>
                <div class="test-section-content">
                    <p><strong>总测试数:</strong> {total}</p>
                    <p><strong>通过:</strong> {passed} | <strong>失败:</strong> {failed}</p>
                    <p><strong>成功率:</strong> {success_rate:.1f}%</p>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {success_rate}%"></div>
                    </div>
"""
            
            if errors:
                html += """
                    <h4>失败详情:</h4>
                    <div class="error-list">
"""
                for error in errors[:10]:  # 只显示前10个错误
                    html += f"""
                        <div class="error-item">
                            <div class="error-title">{error.get('test', '未知测试')}</div>
                            <div class="error-message">{error.get('message', '无错误信息')}</div>
                        </div>
"""
                if len(errors) > 10:
                    html += f"<p>... 还有 {len(errors) - 10} 个错误</p>"
                html += "</div>"
            
            html += """
                </div>
            </div>
"""
            
            return html
        else:
            # 特殊格式的结果（如性能测试）
            return f"""
            <div class="test-section">
                <div class="test-section-header">{test_name}</div>
                <div class="test-section-content">
                    <pre>{json.dumps(result, indent=2, ensure_ascii=False)}</pre>
                </div>
            </div>
"""
    
    def generate_json_report(self, output_file: str = None):
        """
        生成JSON格式的测试报告
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.reports_dir / f'test_summary_{timestamp}.json'
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': sum(result.get('total', 0) for result in self.test_results.values() if isinstance(result, dict) and 'total' in result),
                'total_passed': sum(result.get('passed', 0) for result in self.test_results.values() if isinstance(result, dict) and 'passed' in result),
                'total_failed': sum(result.get('failed', 0) for result in self.test_results.values() if isinstance(result, dict) and 'failed' in result),
            },
            'details': self.test_results
        }
        
        # 计算总体成功率
        if report_data['summary']['total_tests'] > 0:
            report_data['summary']['success_rate'] = report_data['summary']['total_passed'] / report_data['summary']['total_tests'] * 100
        else:
            report_data['summary']['success_rate'] = 0
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON报告已生成: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='生成测试报告汇总')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['html', 'json', 'both'], default='both', help='报告格式')
    parser.add_argument('--base-dir', help='项目根目录')
    
    args = parser.parse_args()
    
    generator = TestReportGenerator(args.base_dir)
    generator.collect_test_results()
    
    if args.format in ['html', 'both']:
        html_output = args.output if args.output and args.output.endswith('.html') else None
        generator.generate_html_report(html_output)
    
    if args.format in ['json', 'both']:
        json_output = args.output if args.output and args.output.endswith('.json') else None
        generator.generate_json_report(json_output)
    
    print("✅ 测试报告生成完成！")


if __name__ == '__main__':
    main()