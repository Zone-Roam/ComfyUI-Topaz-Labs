# 🌐 代理支持使用指南

## 📋 新增功能

已为Topaz Video Enhance节点添加了代理支持，解决网络连接问题。

### 🔧 新增参数

在节点的可选参数中新增了：
- **`proxy_url`**: 代理服务器地址（可选）
  - 格式: `http://proxy.server.com:8080`
  - 留空表示直连
  - 支持HTTP和HTTPS代理

## 🚀 使用方法

### 1. 直连模式（默认）
- 将 `proxy_url` 留空
- 系统将直接连接到Topaz Labs API和AWS S3

### 2. 代理模式
- 在 `proxy_url` 中填入代理地址
- 格式示例：
  ```
  http://proxy.company.com:8080
  https://proxy.company.com:8443
  socks5://proxy.company.com:1080  # 如果代理支持
  ```

## 📊 适用场景

### 🏢 企业网络环境
- 公司防火墙阻止直接访问AWS S3
- 需要通过企业代理服务器访问外网
- 网络策略要求所有外网访问通过代理

### 🌍 地理位置限制
- 某些地区无法直接访问AWS服务
- 使用VPN或代理服务器绕过地理限制
- 提高连接稳定性和速度

### 🔒 安全要求
- 企业安全策略要求所有外网访问记录
- 通过代理服务器进行流量监控
- 统一的网络出口管理

## 🛠️ 常见代理配置

### 1. HTTP代理
```
http://proxy.server.com:8080
```

### 2. HTTPS代理
```
https://proxy.server.com:8443
```

### 3. 带认证的代理
```
http://username:password@proxy.server.com:8080
```

### 4. 本地代理（如Shadowsocks）
```
http://127.0.0.1:1080
socks5://127.0.0.1:1080
```

## 🧪 测试代理连接

### 1. 使用curl测试
```bash
# 测试代理是否能访问Topaz API
curl -x http://proxy.server.com:8080 https://api.topazlabs.com

# 测试代理是否能访问AWS S3
curl -x http://proxy.server.com:8080 https://s3.us-east-1.amazonaws.com
```

### 2. 使用Python测试
```python
import requests

proxies = {
    'http': 'http://proxy.server.com:8080',
    'https': 'http://proxy.server.com:8080'
}

# 测试连接
try:
    response = requests.get('https://api.topazlabs.com', proxies=proxies, timeout=10)
    print(f"代理连接成功: {response.status_code}")
except Exception as e:
    print(f"代理连接失败: {e}")
```

## 📝 使用步骤

### 1. 在ComfyUI中设置
1. 加载Topaz Video Enhance节点
2. 填入API密钥
3. 选择模型和参数
4. **在 `proxy_url` 字段填入代理地址**
5. 运行工作流程

### 2. 观察日志
成功使用代理时，会看到类似日志：
```
Using proxy: http://proxy.server.com:8080
Using proxy for upload: http://proxy.server.com:8080
```

### 3. 故障排除
如果代理连接失败，检查：
- 代理地址格式是否正确
- 代理服务器是否可访问
- 代理是否需要认证
- 防火墙是否允许连接

## ⚠️ 注意事项

### 1. 代理性能
- 代理服务器的带宽和延迟会影响上传速度
- 建议使用高速、稳定的代理服务器
- 避免使用免费的不稳定代理

### 2. 安全考虑
- 不要在代理URL中包含明文密码
- 使用HTTPS代理提高安全性
- 确保代理服务器可信

### 3. 网络稳定性
- 代理连接可能比直连更不稳定
- 系统已内置重试机制
- 如果代理失败，可以尝试直连模式

## 🔧 故障排除

### 问题1: 代理连接超时
**解决方案**:
1. 检查代理地址是否正确
2. 测试代理服务器是否可访问
3. 尝试不同的代理服务器

### 问题2: 代理认证失败
**解决方案**:
1. 确认用户名密码正确
2. 使用URL编码处理特殊字符
3. 联系代理服务器管理员

### 问题3: 上传仍然失败
**解决方案**:
1. 尝试直连模式对比
2. 检查代理服务器的上传限制
3. 使用不同地区的代理服务器

## 📈 性能优化建议

### 1. 选择合适的代理
- 选择地理位置接近AWS S3的代理
- 使用企业级代理服务器
- 避免多层代理转发

### 2. 网络配置
- 确保代理服务器有足够带宽
- 优化代理服务器的连接池设置
- 监控代理服务器的负载

### 3. 备用方案
- 准备多个代理服务器地址
- 在代理失败时快速切换到直连
- 使用VPN作为备用方案

## 🎯 推荐配置

### 企业环境
```
proxy_url: http://corporate-proxy.company.com:8080
```

### 个人VPN
```
proxy_url: http://127.0.0.1:1080
```

### 云代理服务
```
proxy_url: http://proxy.cloudservice.com:8080
```

通过添加代理支持，现在可以在各种网络环境下使用Topaz Labs视频处理功能！
