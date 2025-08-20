#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化部署脚本
支持部署到测试环境和生产环境

使用方法:
python scripts/deploy.py --env test
python scripts/deploy.py --env prod --version v1.2.3
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DeploymentManager:
    """
    部署管理器
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.config_file = self.base_dir / 'deploy' / 'config.json'
        self.config = self._load_config()
        self.deployment_log = []
    
    def _load_config(self) -> Dict:
        """
        加载部署配置
        """
        default_config = {
            "environments": {
                "test": {
                    "name": "测试环境",
                    "host": "test.example.com",
                    "port": 8080,
                    "app_dir": "/var/www/test",
                    "backup_dir": "/var/backups/test",
                    "python_path": "/usr/bin/python3",
                    "requirements_file": "requirements.txt",
                    "pre_deploy_commands": [
                        "pip install -r requirements.txt"
                    ],
                    "post_deploy_commands": [
                        "python manage.py migrate",
                        "python manage.py collectstatic --noinput"
                    ],
                    "health_check_url": "http://test.example.com:8080/health",
                    "rollback_enabled": true
                },
                "prod": {
                    "name": "生产环境",
                    "host": "prod.example.com",
                    "port": 80,
                    "app_dir": "/var/www/prod",
                    "backup_dir": "/var/backups/prod",
                    "python_path": "/usr/bin/python3",
                    "requirements_file": "requirements.txt",
                    "pre_deploy_commands": [
                        "pip install -r requirements.txt"
                    ],
                    "post_deploy_commands": [
                        "python manage.py migrate",
                        "python manage.py collectstatic --noinput"
                    ],
                    "health_check_url": "http://prod.example.com/health",
                    "rollback_enabled": true
                }
            },
            "deployment": {
                "backup_retention_days": 7,
                "health_check_timeout": 30,
                "health_check_retries": 3,
                "deployment_timeout": 300
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载配置文件失败，使用默认配置: {e}")
                return default_config
        else:
            # 创建默认配置文件
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"📝 已创建默认配置文件: {self.config_file}")
            return default_config
    
    def _log(self, message: str, level: str = "INFO"):
        """
        记录部署日志
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def _run_command(self, command: str, cwd: str = None, timeout: int = 60) -> bool:
        """
        执行命令
        """
        try:
            self._log(f"执行命令: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                if result.stdout:
                    self._log(f"命令输出: {result.stdout.strip()}")
                return True
            else:
                self._log(f"命令失败: {result.stderr.strip()}", "ERROR")
                return False
        except subprocess.TimeoutExpired:
            self._log(f"命令超时: {command}", "ERROR")
            return False
        except Exception as e:
            self._log(f"执行命令异常: {e}", "ERROR")
            return False
    
    def validate_environment(self, env: str) -> bool:
        """
        验证环境配置
        """
        if env not in self.config['environments']:
            self._log(f"未知环境: {env}", "ERROR")
            return False
        
        env_config = self.config['environments'][env]
        required_fields = ['name', 'host', 'port', 'app_dir']
        
        for field in required_fields:
            if field not in env_config:
                self._log(f"环境配置缺少必需字段: {field}", "ERROR")
                return False
        
        return True
    
    def create_backup(self, env: str, version: str = None) -> Optional[str]:
        """
        创建备份
        """
        if not version:
            version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        env_config = self.config['environments'][env]
        backup_dir = env_config.get('backup_dir', '/var/backups')
        app_dir = env_config['app_dir']
        
        backup_name = f"backup_{env}_{version}"
        backup_path = f"{backup_dir}/{backup_name}"
        
        self._log(f"创建备份: {backup_path}")
        
        # 创建备份目录
        if not self._run_command(f"mkdir -p {backup_dir}"):
            return None
        
        # 备份应用目录
        if not self._run_command(f"cp -r {app_dir} {backup_path}"):
            return None
        
        # 压缩备份
        if not self._run_command(f"tar -czf {backup_path}.tar.gz -C {backup_dir} {backup_name}"):
            return None
        
        # 删除未压缩的备份目录
        self._run_command(f"rm -rf {backup_path}")
        
        self._log(f"备份创建成功: {backup_path}.tar.gz")
        return f"{backup_path}.tar.gz"
    
    def cleanup_old_backups(self, env: str):
        """
        清理旧备份
        """
        env_config = self.config['environments'][env]
        backup_dir = env_config.get('backup_dir', '/var/backups')
        retention_days = self.config['deployment'].get('backup_retention_days', 7)
        
        self._log(f"清理 {retention_days} 天前的备份")
        
        # 删除旧备份文件
        command = f"find {backup_dir} -name 'backup_{env}_*.tar.gz' -mtime +{retention_days} -delete"
        self._run_command(command)
    
    def deploy_code(self, env: str, version: str = None) -> bool:
        """
        部署代码
        """
        env_config = self.config['environments'][env]
        app_dir = env_config['app_dir']
        
        self._log(f"开始部署到 {env_config['name']}")
        
        # 停止应用服务
        self._log("停止应用服务")
        self._run_command("pkill -f 'python.*app.py' || true")
        
        # 更新代码
        self._log("更新代码")
        if not self._run_command(f"rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' {self.base_dir}/ {app_dir}/"):
            return False
        
        # 安装依赖
        requirements_file = env_config.get('requirements_file', 'requirements.txt')
        if Path(self.base_dir / requirements_file).exists():
            self._log("安装依赖")
            if not self._run_command(f"cd {app_dir} && pip install -r {requirements_file}"):
                return False
        
        # 执行预部署命令
        pre_commands = env_config.get('pre_deploy_commands', [])
        for command in pre_commands:
            self._log(f"执行预部署命令: {command}")
            if not self._run_command(f"cd {app_dir} && {command}"):
                return False
        
        # 启动应用服务
        self._log("启动应用服务")
        port = env_config['port']
        python_path = env_config.get('python_path', 'python3')
        
        # 后台启动应用
        start_command = f"cd {app_dir} && nohup {python_path} app.py --port {port} > app.log 2>&1 &"
        if not self._run_command(start_command):
            return False
        
        # 等待服务启动
        import time
        time.sleep(5)
        
        # 执行后部署命令
        post_commands = env_config.get('post_deploy_commands', [])
        for command in post_commands:
            self._log(f"执行后部署命令: {command}")
            if not self._run_command(f"cd {app_dir} && {command}"):
                self._log(f"后部署命令失败，但继续部署: {command}", "WARNING")
        
        return True
    
    def health_check(self, env: str) -> bool:
        """
        健康检查
        """
        env_config = self.config['environments'][env]
        health_url = env_config.get('health_check_url')
        
        if not health_url:
            self._log("未配置健康检查URL，跳过健康检查", "WARNING")
            return True
        
        timeout = self.config['deployment'].get('health_check_timeout', 30)
        retries = self.config['deployment'].get('health_check_retries', 3)
        
        self._log(f"开始健康检查: {health_url}")
        
        for attempt in range(retries):
            try:
                import requests
                response = requests.get(health_url, timeout=timeout)
                if response.status_code == 200:
                    self._log("健康检查通过")
                    return True
                else:
                    self._log(f"健康检查失败，状态码: {response.status_code}", "WARNING")
            except Exception as e:
                self._log(f"健康检查异常 (尝试 {attempt + 1}/{retries}): {e}", "WARNING")
            
            if attempt < retries - 1:
                import time
                time.sleep(5)
        
        self._log("健康检查失败", "ERROR")
        return False
    
    def rollback(self, env: str, backup_file: str) -> bool:
        """
        回滚部署
        """
        env_config = self.config['environments'][env]
        
        if not env_config.get('rollback_enabled', True):
            self._log("该环境未启用回滚功能", "ERROR")
            return False
        
        app_dir = env_config['app_dir']
        
        self._log(f"开始回滚到备份: {backup_file}")
        
        # 停止应用服务
        self._log("停止应用服务")
        self._run_command("pkill -f 'python.*app.py' || true")
        
        # 删除当前应用目录
        if not self._run_command(f"rm -rf {app_dir}"):
            return False
        
        # 解压备份
        backup_dir = os.path.dirname(backup_file)
        backup_name = os.path.basename(backup_file).replace('.tar.gz', '')
        
        if not self._run_command(f"cd {backup_dir} && tar -xzf {os.path.basename(backup_file)}"):
            return False
        
        # 恢复应用目录
        if not self._run_command(f"mv {backup_dir}/{backup_name} {app_dir}"):
            return False
        
        # 重启应用服务
        self._log("重启应用服务")
        port = env_config['port']
        python_path = env_config.get('python_path', 'python3')
        
        start_command = f"cd {app_dir} && nohup {python_path} app.py --port {port} > app.log 2>&1 &"
        if not self._run_command(start_command):
            return False
        
        # 等待服务启动
        import time
        time.sleep(5)
        
        # 健康检查
        if self.health_check(env):
            self._log("回滚成功")
            return True
        else:
            self._log("回滚后健康检查失败", "ERROR")
            return False
    
    def deploy(self, env: str, version: str = None, skip_backup: bool = False, skip_health_check: bool = False) -> bool:
        """
        执行完整部署流程
        """
        self._log(f"开始部署到环境: {env}")
        
        # 验证环境
        if not self.validate_environment(env):
            return False
        
        backup_file = None
        
        try:
            # 创建备份
            if not skip_backup:
                backup_file = self.create_backup(env, version)
                if not backup_file:
                    self._log("创建备份失败", "ERROR")
                    return False
            
            # 部署代码
            if not self.deploy_code(env, version):
                self._log("代码部署失败", "ERROR")
                
                # 如果有备份，尝试回滚
                if backup_file and not skip_backup:
                    self._log("尝试回滚")
                    self.rollback(env, backup_file)
                
                return False
            
            # 健康检查
            if not skip_health_check:
                if not self.health_check(env):
                    self._log("健康检查失败", "ERROR")
                    
                    # 如果有备份，尝试回滚
                    if backup_file and not skip_backup:
                        self._log("尝试回滚")
                        self.rollback(env, backup_file)
                    
                    return False
            
            # 清理旧备份
            if not skip_backup:
                self.cleanup_old_backups(env)
            
            self._log(f"部署到 {env} 成功完成")
            return True
            
        except Exception as e:
            self._log(f"部署过程中发生异常: {e}", "ERROR")
            
            # 如果有备份，尝试回滚
            if backup_file and not skip_backup:
                self._log("尝试回滚")
                self.rollback(env, backup_file)
            
            return False
    
    def save_deployment_log(self, env: str, version: str = None):
        """
        保存部署日志
        """
        if not version:
            version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        log_dir = self.base_dir / 'deploy' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"deploy_{env}_{version}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.deployment_log))
        
        print(f"📄 部署日志已保存: {log_file}")


def main():
    parser = argparse.ArgumentParser(description='自动化部署脚本')
    parser.add_argument('--env', '-e', required=True, choices=['test', 'prod'], help='部署环境')
    parser.add_argument('--version', '-v', help='版本号')
    parser.add_argument('--skip-backup', action='store_true', help='跳过备份')
    parser.add_argument('--skip-health-check', action='store_true', help='跳过健康检查')
    parser.add_argument('--rollback', help='回滚到指定备份文件')
    parser.add_argument('--base-dir', help='项目根目录')
    
    args = parser.parse_args()
    
    manager = DeploymentManager(args.base_dir)
    
    try:
        if args.rollback:
            # 执行回滚
            success = manager.rollback(args.env, args.rollback)
        else:
            # 执行部署
            success = manager.deploy(
                args.env,
                args.version,
                args.skip_backup,
                args.skip_health_check
            )
        
        # 保存部署日志
        manager.save_deployment_log(args.env, args.version)
        
        if success:
            print("✅ 部署成功完成！")
            sys.exit(0)
        else:
            print("❌ 部署失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ 部署被用户中断")
        manager.save_deployment_log(args.env, args.version)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 部署过程中发生未处理的异常: {e}")
        manager.save_deployment_log(args.env, args.version)
        sys.exit(1)


if __name__ == '__main__':
    main()