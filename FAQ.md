# 常见问题解答 (FAQ)

## 安装和启动相关

### Q1: 如何快速启动项目？

**A:** 
1. 确保已安装Python 3.8+和Node.js 16+
2. 双击运行`start.bat`（Windows）或`./start.sh`（Linux/Mac）
3. 等待依赖自动安装
4. 浏览器自动打开`http://localhost:3000`

### Q2: Python依赖安装失败怎么办？

**A:** 
常见原因和解决方案：

**问题：torch安装失败**
```bash
# 先单独安装PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 再安装其他依赖
pip install -r requirements.txt
```

**问题：网络连接慢**
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 前端依赖安装失败怎么办？

**A:**
```bash
# 清除npm缓存
npm cache clean --force

# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### Q4: 端口被占用怎么办？

**A:**

**修改后端端口（backend/app.py最后一行）：**
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # 改为5001
```

**修改前端端口（frontend/vite.config.js）：**
```javascript
server: {
  port: 3001,  // 改为3001
  proxy: {
    '/api': {
      target: 'http://localhost:5001',  // 同步修改
      changeOrigin: true
    }
  }
}
```

## 数据集相关

### Q5: 支持哪些数据集格式？

**A:** 
- **检测/分割**：YOLO格式（train/images, train/labels, val/images, val/labels）
- **分类**：文件夹分类格式（train/class1, train/class2, val/class1, val/class2）
- **压缩格式**：仅支持ZIP格式

### Q6: 上传的数据集一直显示"处理中"？

**A:**
可能的原因：
1. 数据集格式不正确 - 检查目录结构
2. 标签文件格式错误 - 检查txt文件内容
3. ZIP文件损坏 - 重新压缩上传
4. 后端服务未运行 - 检查后端控制台

**调试方法：**
```bash
# 查看后端日志
cd backend
python app.py
# 查看控制台输出的错误信息
```

### Q7: 如何准备检测数据集？

**A:**
```
dataset/
├── train/
│   ├── images/          # 训练图片
│   │   ├── img1.jpg
│   │   └── ...
│   └── labels/          # YOLO格式标签
│       ├── img1.txt     # 格式: class_id center_x center_y width height
│       └── ...
└── val/
    ├── images/          # 验证图片
    └── labels/          # 验证标签
```

标签文件示例（img1.txt）：
```
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2
```
> 所有坐标值都是归一化的（0-1范围）

### Q8: 数据集大小有限制吗？

**A:**
- 默认限制：500MB
- 修改方法（backend/app.py）：
```python
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 改为1GB
```

## 训练相关

### Q9: 训练任务创建后没有开始？

**A:**
检查清单：
- [ ] 后端服务正在运行
- [ ] 数据集状态为"就绪"
- [ ] 系统有足够的磁盘空间
- [ ] 查看后端控制台的错误信息

### Q10: 训练速度很慢怎么办？

**A:**
优化建议：

**1. 使用GPU加速**
```bash
# 安装CUDA版本的PyTorch（以CUDA 11.8为例）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**2. 调整训练参数**
- 减小图像尺寸：640 -> 416
- 减小批次大小：16 -> 8
- 选择更小的模型：yolo11m -> yolo11n

**3. 检查系统资源**
```bash
# Windows查看GPU使用
nvidia-smi

# 查看CPU和内存
任务管理器 -> 性能
```

### Q11: 训练任务失败了怎么办？

**A:**
调试步骤：

1. **查看任务详情中的日志**
   - 点击任务的"详情"按钮
   - 查看错误信息

2. **常见错误及解决**

   **错误：CUDA out of memory**
   ```
   解决：减小batch_size或img_size
   ```

   **错误：No labels found**
   ```
   解决：检查数据集标签文件是否存在
   ```

   **错误：Invalid label format**
   ```
   解决：检查标签文件格式是否正确（5列数值，空格分隔）
   ```

### Q12: 如何选择合适的训练参数？

**A:**

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 模型规格 | yolo11n/s | 新手推荐，训练快 |
| | yolo11m | 平衡选择 |
| | yolo11l/x | 追求精度 |
| 训练轮数 | 100-300 | 数据集越大，轮数可以越少 |
| | 50-100 | 快速测试 |
| 批次大小 | 16 | 8GB显存 |
| | 32 | 16GB显存 |
| | 8 | 4GB显存或CPU |
| 图像尺寸 | 640 | 标准尺寸 |
| | 416 | 速度优先 |
| | 1280 | 精度优先 |

### Q13: 训练需要多长时间？

**A:**
影响因素：
- 数据集大小
- 训练轮数
- 批次大小
- 硬件配置

**参考时间（1000张图片，100轮）：**
- CPU: 10-20小时
- GTX 1060 (6GB): 2-4小时
- RTX 3060 (12GB): 1-2小时
- RTX 4090 (24GB): 20-40分钟

## 模型相关

### Q14: 如何使用下载的模型？

**A:**
```python
from ultralytics import YOLO

# 加载模型
model = YOLO('path/to/downloaded/model.pt')

# 预测单张图片
results = model('image.jpg')

# 查看结果
results[0].show()

# 保存结果
results[0].save('output.jpg')

# 预测视频
results = model('video.mp4')

# 批量预测
results = model(['img1.jpg', 'img2.jpg', 'img3.jpg'])
```

### Q15: 模型文件很大怎么办？

**A:**
优化方法：

1. **选择更小的模型**
   - yolo11x: ~130MB
   - yolo11l: ~80MB
   - yolo11m: ~50MB
   - yolo11s: ~22MB
   - yolo11n: ~6MB

2. **模型量化**（需要额外代码）
   ```python
   # INT8量化示例
   model.export(format='onnx', int8=True)
   ```

### Q16: 可以导出其他格式吗？

**A:**
当前版本暂不支持，但可以手动导出：

```python
from ultralytics import YOLO

model = YOLO('your_model.pt')

# 导出ONNX
model.export(format='onnx')

# 导出TensorRT
model.export(format='engine')

# 导出TFLite
model.export(format='tflite')

# 导出CoreML
model.export(format='coreml')
```

## 性能和优化

### Q17: 如何提高检测精度？

**A:**
优化策略：

1. **数据集质量**
   - 增加数据集数量（越多越好）
   - 提高标注质量（边界框要准确）
   - 数据均衡（各类别数量相近）

2. **训练参数**
   - 增加训练轮数：100 -> 200-300
   - 使用更大的模型：yolo11n -> yolo11m/l
   - 增加图像尺寸：640 -> 1280

3. **数据增强**（在代码中配置）
   ```python
   # 需要修改train_service.py
   model.train(
       data=data_yaml,
       augment=True,
       mosaic=1.0,
       mixup=0.5,
       # ...其他参数
   )
   ```

### Q18: 系统占用内存太大？

**A:**
优化方案：

1. **减小批次大小**
   - 从16降到8或4

2. **减小图像缓存**
   ```python
   # 修改train_service.py
   model.train(
       data=data_yaml,
       cache=False,  # 不缓存图像到内存
       # ...
   )
   ```

3. **关闭其他程序**
   - 训练时关闭浏览器多余标签页
   - 关闭其他应用程序

## 错误处理

### Q19: "找不到模块 'ultralytics'" 错误？

**A:**
```bash
# 激活虚拟环境
cd backend
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac

# 安装ultralytics
pip install ultralytics
```

### Q20: "No module named 'flask_cors'" 错误？

**A:**
```bash
# 确保安装了所有依赖
pip install -r requirements.txt
```

### Q21: 前端显示"网络错误"？

**A:**
检查清单：
1. 后端服务是否运行（应该在http://localhost:5000）
2. 浏览器控制台是否有CORS错误
3. 防火墙是否阻止了连接

**测试后端：**
```bash
# 在浏览器访问
http://localhost:5000/api/stats
# 应该返回JSON数据
```

### Q22: 页面显示空白？

**A:**
1. 打开浏览器开发者工具（F12）
2. 查看Console标签的错误信息
3. 检查Network标签，确认API请求正常
4. 清除浏览器缓存，刷新页面

## 高级使用

### Q23: 如何同时训练多个任务？

**A:**
当前版本支持多任务，但建议：
- 根据GPU显存限制数量
- 每个任务使用不同的数据集
- 监控系统资源使用

### Q24: 可以使用预训练模型吗？

**A:**
可以，修改`train_service.py`：
```python
# 使用预训练模型
model = YOLO('path/to/pretrained.pt')  # 而不是 'yolo11n.pt'
```

### Q25: 如何在远程服务器上运行？

**A:**

1. **修改后端监听地址（已配置）**
   ```python
   # app.py已经配置为0.0.0.0
   app.run(host='0.0.0.0', port=5000)
   ```

2. **修改前端API地址**
   ```javascript
   // frontend/src/utils/request.js
   baseURL: 'http://your-server-ip:5000/api'
   ```

3. **配置防火墙**
   ```bash
   # 开放端口
   sudo ufw allow 5000
   sudo ufw allow 3000
   ```

## 数据安全

### Q26: 上传的数据集会被保存多久？

**A:**
- 数据集永久保存，直到手动删除
- 存储位置：`backend/datasets/`
- 建议定期清理不需要的数据集

### Q27: 训练数据会泄露吗？

**A:**
- 所有数据都在本地服务器
- 不会上传到云端
- 建议在内网环境使用

## 其他

### Q28: 支持哪些图像格式？

**A:**
- JPG/JPEG
- PNG
- BMP（自动转换）

### Q29: 可以在CPU上训练吗？

**A:**
可以，但速度很慢：
- GPU: 1小时 ≈ CPU: 10-20小时
- 建议CPU用户：
  - 使用小数据集测试
  - 选择yolo11n模型
  - 减少训练轮数

### Q30: 如何获得帮助？

**A:**
1. 查看文档：
   - README.md
   - QUICK_START.md
   - DATASET_GUIDE.md
   - PROJECT_INFO.md

2. 检查日志：
   - 后端控制台输出
   - 浏览器开发者工具

3. 提交Issue：
   - 描述问题
   - 附上错误日志
   - 说明环境信息

---

## 快速参考

### 启动命令
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### 默认端口
- 后端: http://localhost:5000
- 前端: http://localhost:3000

### 重要目录
```
backend/datasets/  # 数据集存储
backend/models/    # 模型存储
backend/runs/      # 训练输出
backend/uploads/   # 临时上传
```

### 日志位置
- 后端日志: 控制台输出
- 训练日志: 任务详情页面
- 系统日志: runs/task_*/train/

---

**找不到答案？** 请查看完整文档或提交Issue！
