#!/usr/bin/env python3
"""
测试网络连接的脚本
检查是否能够访问Topaz Labs API和AWS S3
"""

import requests
import socket
import time
from urllib.parse import urlparse

def test_dns_resolution(hostname):
    """测试DNS解析"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS解析成功: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {hostname} - {e}")
        return False

def test_tcp_connection(hostname, port=443):
    """测试TCP连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP连接成功: {hostname}:{port}")
            return True
        else:
            print(f"❌ TCP连接失败: {hostname}:{port}")
            return False
    except Exception as e:
        print(f"❌ TCP连接异常: {hostname}:{port} - {e}")
        return False

def test_http_connection(url, timeout=30):
    """测试HTTP连接"""
    try:
        print(f"🔍 测试HTTP连接: {url}")
        response = requests.get(url, timeout=timeout)
        print(f"✅ HTTP连接成功: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ HTTP连接超时: {url}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ HTTP连接错误: {url} - {e}")
        return False
    except Exception as e:
        print(f"❌ HTTP连接异常: {url} - {e}")
        return False

def test_upload_simulation(upload_url):
    """模拟上传测试（不实际上传数据）"""
    try:
        print(f"🔍 测试上传连接: {urlparse(upload_url).netloc}")
        
        # 只发送HEAD请求测试连接
        response = requests.head(upload_url, timeout=30)
        print(f"✅ 上传连接测试成功: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print(f"❌ 上传连接超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 上传连接错误: {e}")
        return False
    except Exception as e:
        print(f"⚠️ 上传连接测试: {e}")
        # HEAD请求可能返回错误，但连接是通的
        return True

def main():
    """主测试函数"""
    print("🌐 网络连接测试")
    print("=" * 50)
    
    # 测试目标
    test_targets = [
        ("Topaz Labs API", "api.topazlabs.com"),
        ("AWS S3 (US East)", "s3.us-east-1.amazonaws.com"),
        ("AWS S3 VideoCloud", "videocloud-prod-main-useast1-bucket-data.s3.us-east-1.amazonaws.com"),
        ("Google DNS", "8.8.8.8"),
        ("Cloudflare DNS", "1.1.1.1")
    ]
    
    print("🔍 测试 1: DNS解析")
    dns_results = []
    for name, hostname in test_targets:
        if hostname in ["8.8.8.8", "1.1.1.1"]:
            continue  # 跳过IP地址
        result = test_dns_resolution(hostname)
        dns_results.append((name, result))
    
    print("\n🔍 测试 2: TCP连接")
    tcp_results = []
    for name, hostname in test_targets:
        if hostname in ["8.8.8.8", "1.1.1.1"]:
            continue  # 跳过IP地址
        result = test_tcp_connection(hostname)
        tcp_results.append((name, result))
    
    print("\n🔍 测试 3: HTTP连接")
    http_tests = [
        ("Topaz Labs API", "https://api.topazlabs.com"),
        ("AWS S3", "https://s3.us-east-1.amazonaws.com"),
        ("Google", "https://www.google.com"),
    ]
    
    http_results = []
    for name, url in http_tests:
        result = test_http_connection(url)
        http_results.append((name, result))
    
    print("\n🔍 测试 4: 网络速度")
    try:
        start_time = time.time()
        response = requests.get("https://www.google.com", timeout=10)
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        print(f"✅ 网络延迟: {latency:.0f}ms")
    except Exception as e:
        print(f"❌ 网络速度测试失败: {e}")
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    
    dns_passed = sum(1 for _, result in dns_results if result)
    tcp_passed = sum(1 for _, result in tcp_results if result)
    http_passed = sum(1 for _, result in http_results if result)
    
    print(f"DNS解析: {dns_passed}/{len(dns_results)} 通过")
    print(f"TCP连接: {tcp_passed}/{len(tcp_results)} 通过")
    print(f"HTTP连接: {http_passed}/{len(http_results)} 通过")
    
    if dns_passed == len(dns_results) and tcp_passed == len(tcp_results):
        print("\n✅ 网络连接正常，上传问题可能是:")
        print("   1. 临时网络拥塞")
        print("   2. 防火墙/代理设置")
        print("   3. ISP限制")
        print("   4. 文件过大导致超时")
        print("\n💡 建议:")
        print("   1. 重试上传")
        print("   2. 检查防火墙设置")
        print("   3. 尝试使用VPN")
        print("   4. 减小视频文件大小")
    else:
        print("\n❌ 网络连接存在问题")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 检查DNS设置")
        print("   3. 检查防火墙/代理设置")
        print("   4. 联系网络管理员")

if __name__ == "__main__":
    main()
