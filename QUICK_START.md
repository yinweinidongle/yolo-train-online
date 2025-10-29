# YOLOv11在线训练平台 - 快速启动指南

## Windows系统快速启动

### 第一次运行

1. **安装后端依赖**

打开PowerShell或命令提示符，执行：

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **安装前端依赖**

打开新的终端窗口：

```bash
cd frontend
npm install
```

### 启动服务

**方法一：手动启动（推荐用于开发）**

1. 启动后端（终端1）：
```bash
cd backend
venv\Scripts\activate
python app.py
```

2. 启动前端（终端2）：
```bash
cd frontend
npm run dev
```

**方法二：使用启动脚本**

创建 `start.bat` 文件：

```batch
@echo off
echo Starting YOLOv11 Training Platform...

start "Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"
timeout /t 3
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Services started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
pause
```

双击运行 `start.bat` 即可启动所有服务。

### 访问应用

在浏览器中打开：`http://localhost:3000`

## Linux/Mac系统快速启动

### 第一次运行

1. **安装后端依赖**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **安装前端依赖**

```bash
cd frontend
npm install
```

### 启动服务

创建 `start.sh` 文件：

```bash
#!/bin/bash

echo "Starting YOLOv11 Training Platform..."

# 启动后端
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Services started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"

# 等待用户输入停止
read -p "Press Enter to stop services..."

# 停止服务
kill $BACKEND_PID
kill $FRONTEND_PID
```

运行：

```bash
chmod +x start.sh
./start.sh
```

## 使用Docker（可选）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - ./backend/datasets:/app/datasets
      - ./backend/models:/app/models
      - ./backend/runs:/app/runs
    environment:
      - FLASK_ENV=development

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

启动：

```bash
docker-compose up
```

## 常见问题排查

### 端口占用

如果5000或3000端口被占用：

**修改后端端口（app.py最后一行）：**
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

**修改前端端口（vite.config.js）：**
```javascript
server: {
  port: 3001
}
```

### Python依赖安装失败

如果torch安装失败，可以先手动安装：

```bash
# CPU版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU版本（CUDA 11.8）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

然后再安装其他依赖：
```bash
pip install -r requirements.txt
```

### 前端依赖安装慢

使用国内镜像源：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

## 测试数据集

可以从以下渠道获取测试数据集：

1. **COCO数据集**（目标检测）
   - https://cocodataset.org/

2. **ImageNet**（图像分类）
   - https://www.image-net.org/

3. **自定义数据集**
   - 使用labelImg、CVAT等工具标注

准备好数据集后，按照README中的格式要求打包成ZIP文件上传。

## 性能优化建议

1. **GPU加速**：安装CUDA版本的PyTorch可大幅提升训练速度
2. **批次大小**：根据显存调整，8GB显存建议batch_size=8-16
3. **图像尺寸**：较小的图像尺寸训练更快，但精度可能降低
4. **模型选择**：yolo11n最快，yolo11x最准确但最慢

## 下一步

1. 阅读完整的 [README.md](README.md)
2. 准备数据集并上传
3. 开始第一个训练任务
4. 查看训练结果并下载模型

祝使用愉快！🎉
