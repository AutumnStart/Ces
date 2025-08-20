# 性能测试文档

本目录包含商城系统的完整性能测试套件，提供多种性能测试工具和方法。

## 📁 文件结构

```
tests/performance/
├── README.md                    # 本文件 - 性能测试说明
├── locustfile.py               # Locust负载测试配置
├── test_performance.py         # pytest性能测试用例
├── run_performance_tests.py    # 性能测试运行脚本
└── reports/                    # 测试报告目录（自动生成）
    ├── locust_*.html           # Locust HTML报告
    ├── locust_*_stats.csv      # Locust统计数据
    ├── pytest_*.html          # pytest HTML报告
    └── performance_summary_*.json  # 汇总报告
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 自动安装所有依赖
python tests/performance/run_performance_tests.py --install-deps

# 或手动安装
pip install pytest pytest-benchmark pytest-xdist pytest-html pytest-json-report locust requests
```

### 2. 启动应用程序

确保商城应用程序正在运行：

```bash
cd app
python app.py
```

应用程序应该在 `http://localhost:5000` 上运行。

### 3. 运行性能测试

```bash
# 快速性能测试（推荐首次使用）
python tests/performance/run_performance_tests.py --quick

# 完整性能测试
python tests/performance/run_performance_tests.py --full

# 压力测试
python tests/performance/run_performance_tests.py --stress

# 仅运行Locust负载测试
python tests/performance/run_performance_tests.py --locust --users 20 --duration 120s
```

## 📊 测试类型说明

### 1. 基础性能测试 (pytest)

**文件**: `test_performance.py`

**测试内容**:
- 页面响应时间测试
- 并发访问测试
- 压力测试
- 内存泄漏检测

**运行方式**:
```bash
# 运行所有pytest性能测试
pytest tests/performance/test_performance.py -v

# 仅运行基准测试
pytest tests/performance/test_performance.py -v --benchmark-only

# 并发测试
pytest tests/performance/test_performance.py -v -n 4

# 运行特定测试
pytest tests/performance/test_performance.py -v -k "homepage"
```

**性能基准**:
- 首页响应时间: < 1.0s (目标: 0.5s)
- 商品页面响应时间: < 2.0s (目标: 1.0s)
- 商品详情响应时间: < 1.5s (目标: 0.8s)
- 登录页面响应时间: < 2.0s (目标: 1.0s)
- 搜索功能响应时间: < 3.0s (目标: 1.5s)

### 2. 负载测试 (Locust)

**文件**: `locustfile.py`

**测试内容**:
- 模拟真实用户行为
- 多种用户类型（普通用户、管理员、压力测试用户）
- 不同频率的操作任务

**用户行为模拟**:
- **普通用户** (ShopUser): 浏览商品、搜索、购物车操作
- **管理员用户** (AdminUser): 管理后台操作
- **快速测试用户** (QuickTestUser): 基础功能验证
- **压力测试用户** (StressTestUser): 高频访问测试

**运行方式**:
```bash
# 命令行模式（推荐）
locust -f tests/performance/locustfile.py --host=http://localhost:5000 --users 10 --spawn-rate 2 --run-time 60s --headless

# Web界面模式
locust -f tests/performance/locustfile.py --host=http://localhost:5000 --web-host=0.0.0.0 --web-port=8089
# 然后访问 http://localhost:8089

# 使用运行脚本
python tests/performance/run_performance_tests.py --locust --users 20 --duration 120s
```

## 🔧 测试配置

### 性能基准配置

在 `test_performance.py` 中的 `PerformanceTestConfig` 类：

```python
class PerformanceTestConfig:
    BASE_URL = 'http://localhost:5000'
    TIMEOUT = 10  # 请求超时时间（秒）
    MAX_RESPONSE_TIME = 2.0  # 最大可接受响应时间（秒）
    CONCURRENT_USERS = 10  # 并发用户数
    REQUESTS_PER_USER = 5  # 每个用户的请求数
    
    # 性能基准
    BENCHMARKS = {
        'homepage': {'max_time': 1.0, 'target_time': 0.5},
        'products': {'max_time': 2.0, 'target_time': 1.0},
        # ... 更多配置
    }
```

### Locust配置

在 `locustfile.py` 中可以调整：

```python
class ShopUser(HttpUser):
    wait_time = between(1, 3)  # 用户请求间隔时间
    
    @task(10)  # 任务权重
    def view_homepage(self):
        # 任务实现
```

## 📈 测试报告

### pytest报告

- **HTML报告**: 包含详细的测试结果和图表
- **JSON报告**: 机器可读的测试数据
- **基准报告**: 性能基准测试结果

### Locust报告

- **HTML报告**: 包含请求统计、响应时间分布、失败率等
- **CSV数据**: 详细的统计数据，可用于进一步分析

### 汇总报告

运行脚本会生成JSON格式的汇总报告，包含：
- 所有测试的执行结果
- 总体统计信息
- 报告文件路径

## 🎯 测试场景

### 场景1: 日常性能监控

```bash
# 每日快速检查
python tests/performance/run_performance_tests.py --quick
```

**目的**: 快速验证系统基本性能
**频率**: 每日或每次部署后
**时间**: 约2-3分钟

### 场景2: 版本发布前测试

```bash
# 完整性能测试
python tests/performance/run_performance_tests.py --full
```

**目的**: 全面评估系统性能
**频率**: 版本发布前
**时间**: 约10-15分钟

### 场景3: 容量规划测试

```bash
# 压力测试
python tests/performance/run_performance_tests.py --stress
```

**目的**: 确定系统容量上限
**频率**: 月度或季度
**时间**: 约15-20分钟

### 场景4: 负载测试

```bash
# 模拟真实负载
python tests/performance/run_performance_tests.py --locust --users 50 --duration 300s
```

**目的**: 模拟生产环境负载
**频率**: 重大更新前
**时间**: 5-10分钟

## 📊 性能指标说明

### 响应时间指标

- **平均响应时间**: 所有请求的平均响应时间
- **中位数响应时间**: 50%的请求响应时间
- **P95响应时间**: 95%的请求响应时间
- **P99响应时间**: 99%的请求响应时间
- **最大响应时间**: 最慢的请求响应时间

### 吞吐量指标

- **RPS (Requests Per Second)**: 每秒请求数
- **并发用户数**: 同时访问的用户数
- **成功率**: 成功请求的百分比

### 资源使用指标

- **内存使用**: 应用程序内存消耗
- **CPU使用**: 处理器使用率
- **网络带宽**: 网络传输量

## 🚨 性能问题诊断

### 常见性能问题

1. **响应时间过长**
   - 检查数据库查询效率
   - 优化静态资源加载
   - 考虑添加缓存

2. **并发性能差**
   - 检查数据库连接池配置
   - 优化锁机制
   - 考虑异步处理

3. **内存泄漏**
   - 运行内存泄漏检测测试
   - 检查对象生命周期管理
   - 监控长时间运行的进程

### 性能优化建议

1. **前端优化**
   - 压缩CSS/JS文件
   - 优化图片大小
   - 使用CDN

2. **后端优化**
   - 数据库索引优化
   - 查询语句优化
   - 缓存策略

3. **架构优化**
   - 负载均衡
   - 微服务架构
   - 异步处理

## 🔍 故障排除

### 常见问题

1. **应用程序未运行**
   ```
   ❌ 无法连接到应用程序: http://localhost:5000
   ```
   **解决方案**: 启动应用程序 `python app/app.py`

2. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'locust'
   ```
   **解决方案**: 安装依赖 `pip install locust`

3. **端口冲突**
   ```
   Address already in use
   ```
   **解决方案**: 更改端口或停止占用端口的进程

4. **测试超时**
   ```
   requests.exceptions.Timeout
   ```
   **解决方案**: 增加超时时间或检查网络连接

### 调试技巧

1. **启用详细日志**
   ```bash
   pytest tests/performance/test_performance.py -v -s
   ```

2. **单独运行测试**
   ```bash
   pytest tests/performance/test_performance.py::TestBasicPerformance::test_homepage_response_time -v
   ```

3. **检查应用程序日志**
   ```bash
   # 查看应用程序输出
   tail -f app.log
   ```

## 📋 最佳实践

### 测试执行

1. **测试前准备**
   - 确保测试环境稳定
   - 清理测试数据
   - 重启应用程序

2. **测试执行**
   - 从快速测试开始
   - 逐步增加负载
   - 监控系统资源

3. **结果分析**
   - 对比历史数据
   - 识别性能趋势
   - 记录优化措施

### 持续集成

1. **自动化执行**
   ```yaml
   # CI/CD配置示例
   performance_test:
     script:
       - python tests/performance/run_performance_tests.py --quick
   ```

2. **性能回归检测**
   - 设置性能基准
   - 自动对比结果
   - 性能下降时告警

3. **报告归档**
   - 保存历史报告
   - 生成趋势图表
   - 定期清理旧报告

## 📞 支持和联系

### 技术支持

- **性能问题**: 联系开发团队
- **测试工具**: 联系测试团队
- **环境问题**: 联系运维团队

### 相关资源

- [Locust官方文档](https://docs.locust.io/)
- [pytest-benchmark文档](https://pytest-benchmark.readthedocs.io/)
- [性能测试最佳实践](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**文档版本**: v1.0  
**创建日期**: 2024年  
**最后更新**: 2024年  
**维护团队**: 测试团队  

> 💡 **提示**: 建议先运行快速测试熟悉工具，然后根据需要选择合适的测试类型。

> ⚠️ **注意**: 压力测试可能会对系统造成较大负载，请在合适的环境中执行。