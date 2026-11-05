# Topaz Labs 异步模式使用指南

## 什么是异步模式？

**异步模式 (use_async = True)**：
- 任务提交到 Topaz 服务器队列
- 立即返回任务ID，不阻塞界面
- 后台轮询任务状态直到完成
- 适合大图像或复杂处理

**同步模式 (use_async = False)**：
- 直接等待处理完成
- 保持连接直到结果返回
- 适合小图像或快速处理

## 异步模式工作流程

### 1. 提交任务
```
🔄 Starting async job polling (Process ID: abc123)
⏱️ Estimated completion time: 45 seconds
📡 Will check status every 5 seconds...
```

### 2. 轮询状态
```
📊 Poll #1 (5s elapsed): Status = queued
📊 Poll #2 (10s elapsed): Status = processing
📊 Poll #3 (15s elapsed): Status = processing
...
```

### 3. 完成下载
```
✅ Job completed! Downloading result from: https://api.topazlabs.com/...
🎉 Successfully downloaded 2,456,789 bytes of image data!
```

## 如何获得图像？

### 在 ComfyUI 中：
1. **设置节点**：将 `use_async` 设为 `True`
2. **点击 Queue Prompt**：任务开始处理
3. **查看控制台**：观察进度信息
4. **等待完成**：图像会自动出现在输出节点

### 预期等待时间：
- **小图像 (< 1MP)**：10-30秒
- **中等图像 (1-4MP)**：30-60秒  
- **大图像 (> 4MP)**：1-3分钟
- **超大图像**：可能更长

## 故障排除

### 如果长时间没有结果：
1. 检查控制台是否有错误信息
2. 确认 API key 是否正确
3. 检查网络连接
4. 尝试切换到同步模式测试

### 常见错误：
- `Job timed out`：任务超时，尝试减小图像尺寸
- `Failed to load image data`：下载失败，检查网络
- `API returned error`：API 错误，检查参数设置

## 建议

- **首次使用**：建议先用小图像测试异步模式
- **大批量处理**：使用异步模式避免超时
- **快速预览**：使用同步模式获得即时结果
- **网络不稳定**：优先使用同步模式
