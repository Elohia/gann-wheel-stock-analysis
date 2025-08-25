#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口测试用例

测试股票分析系统的RESTful API接口功能。

Author: AI Assistant
Date: 2024
"""

import unittest
import requests
import json
import time
from typing import Dict, Any


class TestStockAnalysisAPI(unittest.TestCase):
    """股票分析API测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.base_url = "http://localhost:8001"
        cls.test_symbol = "000001.SZ"
        cls.test_symbols = ["000001.SZ", "600036.SH"]
        
        # 等待服务器启动
        cls._wait_for_server()
    
    @classmethod
    def _wait_for_server(cls, timeout: int = 30):
        """等待服务器启动"""
        print("等待API服务器启动...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("API服务器已启动")
                    return
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        raise Exception(f"API服务器在 {timeout} 秒内未启动")
    
    def setUp(self):
        """每个测试方法前的初始化"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def tearDown(self):
        """每个测试方法后的清理"""
        self.session.close()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        return response
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = self._make_request('GET', '/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
    
    def test_health_check(self):
        """测试健康检查"""
        response = self._make_request('GET', '/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('system_info', data)
        
        system_info = data['system_info']
        self.assertIn('service_name', system_info)
        self.assertIn('version', system_info)
        self.assertIn('status', system_info)
        self.assertEqual(system_info['status'], 'running')
    
    def test_list_stocks(self):
        """测试获取股票列表"""
        response = self._make_request('GET', '/stocks')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('stocks', data)
        self.assertIn('total_count', data)
        self.assertIsInstance(data['stocks'], list)
        self.assertIsInstance(data['total_count'], int)
    
    def test_list_stocks_with_params(self):
        """测试带参数的股票列表获取"""
        params = {'limit': 5, 'offset': 0}
        response = self._make_request('GET', '/stocks', params=params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertLessEqual(len(data['stocks']), 5)
    
    def test_fetch_stock_data(self):
        """测试获取股票数据"""
        payload = {
            'symbol': self.test_symbol,
            'period': '1y'
        }
        
        response = self._make_request('POST', '/stocks/data', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        
        if data['data']:
            stock_data = data['data']
            self.assertEqual(stock_data['symbol'], self.test_symbol)
            self.assertIn('start_date', stock_data)
            self.assertIn('end_date', stock_data)
    
    def test_fetch_stock_data_invalid_symbol(self):
        """测试获取无效股票代码的数据"""
        payload = {
            'symbol': 'INVALID.XX',
            'period': '1y'
        }
        
        response = self._make_request('POST', '/stocks/data', json=payload)
        # 应该返回400或500错误
        self.assertIn(response.status_code, [400, 500])
    
    def test_analyze_single_stock(self):
        """测试单股票分析"""
        payload = {
            'symbol': self.test_symbol,
            'analysis_type': 'all',
            'auto_fetch': True
        }
        
        response = self._make_request('POST', '/analysis/single', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
        
        if data['result']:
            result = data['result']
            self.assertEqual(result['symbol'], self.test_symbol)
            self.assertIn('analysis_date', result)
    
    def test_analyze_single_stock_gann_only(self):
        """测试仅江恩分析"""
        payload = {
            'symbol': self.test_symbol,
            'analysis_type': 'gann',
            'auto_fetch': True
        }
        
        response = self._make_request('POST', '/analysis/single', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        if data['result']:
            result = data['result']
            # 应该只有江恩分析结果
            self.assertIn('gann_analysis', result)
    
    def test_analyze_single_stock_volume_price_only(self):
        """测试仅量价分析"""
        payload = {
            'symbol': self.test_symbol,
            'analysis_type': 'volume_price',
            'auto_fetch': True
        }
        
        response = self._make_request('POST', '/analysis/single', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        if data['result']:
            result = data['result']
            # 应该只有量价分析结果
            self.assertIn('volume_price_analysis', result)
    
    def test_batch_analysis(self):
        """测试批量分析"""
        payload = {
            'symbols': self.test_symbols,
            'analysis_type': 'all',
            'auto_fetch': True
        }
        
        response = self._make_request('POST', '/analysis/batch', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data)
        self.assertIn('success_count', data)
        self.assertIn('failed_symbols', data)
        
        self.assertIsInstance(data['results'], list)
        self.assertIsInstance(data['success_count'], int)
        self.assertIsInstance(data['failed_symbols'], list)
    
    def test_get_analysis_by_symbol(self):
        """测试通过GET方法获取分析结果"""
        params = {
            'analysis_type': 'all',
            'auto_fetch': True
        }
        
        response = self._make_request('GET', f'/analysis/{self.test_symbol}', params=params)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('result', data)
    
    def test_invalid_analysis_type(self):
        """测试无效的分析类型"""
        payload = {
            'symbol': self.test_symbol,
            'analysis_type': 'invalid_type',
            'auto_fetch': True
        }
        
        response = self._make_request('POST', '/analysis/single', json=payload)
        # 应该返回422验证错误
        self.assertEqual(response.status_code, 422)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        payload = {
            'analysis_type': 'all',
            'auto_fetch': True
            # 缺少symbol字段
        }
        
        response = self._make_request('POST', '/analysis/single', json=payload)
        # 应该返回422验证错误
        self.assertEqual(response.status_code, 422)
    
    def test_invalid_json(self):
        """测试无效的JSON数据"""
        response = self._make_request(
            'POST', 
            '/analysis/single', 
            data="invalid json",
            headers={'Content-Type': 'application/json'}
        )
        # 应该返回422验证错误
        self.assertEqual(response.status_code, 422)
    
    def test_nonexistent_endpoint(self):
        """测试不存在的端点"""
        response = self._make_request('GET', '/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_method_not_allowed(self):
        """测试不允许的HTTP方法"""
        response = self._make_request('DELETE', '/health')
        self.assertEqual(response.status_code, 405)


class TestAPIPerformance(unittest.TestCase):
    """API性能测试类"""
    
    def setUp(self):
        self.base_url = "http://localhost:8001"
        self.session = requests.Session()
    
    def tearDown(self):
        self.session.close()
    
    def test_health_check_response_time(self):
        """测试健康检查响应时间"""
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, "健康检查响应时间应小于2秒")
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = self.session.get(f"{self.base_url}/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # 创建10个并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        self.assertEqual(success_count, 10, "所有并发请求都应该成功")


def run_tests():
    """运行所有测试"""
    print("开始运行API测试...")
    print("注意: 请确保API服务器正在运行 (python run_api.py)")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加功能测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestStockAnalysisAPI))
    
    # 添加性能测试
    test_suite.addTests(loader.loadTestsFromTestCase(TestAPIPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print(f"测试完成: 运行 {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)