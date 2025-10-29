# YOLOv11在线训练平台 - 项目说明

## 项目概述

这是一个基于Web的YOLOv11模型在线训练管理平台，支持目标检测、图像分类和图像分割三种任务类型。用户可以通过浏览器上传数据集、配置训练参数、监控训练进度，并下载训练完成的模型。

## 核心功能

### 1. 数据集管理模块
- ✅ 支持ZIP格式数据集上传
- ✅ 自动解析和验证数据集结构
- ✅ 支持检测、分类、分割三种数据集类型
- ✅ 数据集统计信息展示
- ✅ 数据集删除功能

### 2. 模型训练模块
- ✅ 支持YOLOv11n/s/m/l/x五种模型规格
- ✅ 灵活的训练参数配置（轮数、批次、图像尺寸）
- ✅ 异步训练任务执行
- ✅ 实时训练进度显示
- ✅ 训练日志记录
- ✅ 训练任务停止功能

### 3. 模型管理模块
- ✅ 训练完成模型自动保存
- ✅ 模型列表查看
- ✅ 模型详情展示
- ✅ 模型下载功能
- ✅ 模型删除管理

### 4. 仪表盘模块
- ✅ 平台统计信息概览
- ✅ 最近数据集展示
- ✅ 最近训练任务展示
- ✅ 快速操作入口

## 技术架构

### 前端架构
```
Vue3 + Ant Design Vue
├── 路由管理: Vue Router 4
├── 状态管理: Pinia
├── HTTP请求: Axios
├── 构建工具: Vite
└── UI组件库: Ant Design Vue 4
```

### 后端架构
```
Flask + SQLite + YOLOv11
├── Web框架: Flask 3.0
├── 数据库: SQLite (SQLAlchemy ORM)
├── 深度学习: YOLOv11 (Ultralytics)
├── 异步训练: Threading
└── 跨域支持: Flask-CORS
```

## 文件结构说明

```
yolo-online/
├── backend/                       # 后端目录
│   ├── app.py                    # Flask主应用 - API路由定义
│   ├── models.py                 # 数据库模型（Dataset、Model、TrainingTask）
│   ├── train_service.py          # 训练服务 - 核心训练逻辑
│   ├── requirements.txt          # Python依赖列表
│   ├── datasets/                 # 数据集存储目录
│   ├── models/                   # 训练完成的模型存储
│   ├── runs/                     # 训练输出和日志
│   └── uploads/                  # 临时文件上传目录
│
├── frontend/                      # 前端目录
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   │   ├── Dashboard.vue    # 仪表盘 - 概览页面
│   │   │   ├── Datasets.vue     # 数据集管理页面
│   │   │   ├── Training.vue     # 训练任务管理页面
│   │   │   └── Models.vue       # 模型管理页面
│   │   ├── layouts/
│   │   │   └── MainLayout.vue   # 主布局 - 侧边栏+内容区
│   │   ├── api/
│   │   │   └── index.js         # API接口封装
│   │   ├── utils/
│   │   │   └── request.js       # Axios封装
│   │   ├── router/
│   │   │   └── index.js         # 路由配置
│   │   ├── App.vue              # 根组件
│   │   └── main.js              # 入口文件
│   ├── public/
│   │   └── logo.svg             # Logo图标
│   ├── package.json             # 前端依赖配置
│   ├── vite.config.js           # Vite配置
│   └── index.html               # HTML模板
│
├── README.md                      # 完整项目文档
├── QUICK_START.md                 # 快速启动指南
├── PROJECT_INFO.md                # 本文件 - 项目说明
├── .gitignore                     # Git忽略配置
├── start.bat                      # Windows启动脚本
└── start.sh                       # Linux/Mac启动脚本
```

## API接口列表

### 统计信息
- `GET /api/stats` - 获取平台统计信息

### 数据集接口
- `GET /api/datasets` - 获取所有数据集
- `GET /api/datasets/<id>` - 获取单个数据集详情
- `POST /api/datasets/upload` - 上传数据集
- `DELETE /api/datasets/<id>` - 删除数据集

### 模型接口
- `GET /api/models` - 获取所有模型
- `GET /api/models/<id>` - 获取模型详情
- `GET /api/models/<id>/download` - 下载模型文件
- `DELETE /api/models/<id>` - 删除模型

### 训练任务接口
- `GET /api/tasks` - 获取所有训练任务
- `GET /api/tasks/<id>` - 获取任务详情
- `POST /api/tasks/create` - 创建训练任务
- `POST /api/tasks/<id>/stop` - 停止训练任务
- `GET /api/tasks/<id>/progress` - 获取训练进度

## 数据库设计

### Dataset表 - 数据集
```sql
- id: 主键
- name: 数据集名称
- task_type: 任务类型 (detect/classify/segment)
- description: 描述
- path: 存储路径
- file_count: 文件数量
- size: 大小（字节）
- format: 格式
- status: 状态 (processing/ready/error)
- created_at: 创建时间
- updated_at: 更新时间
```

### Model表 - 模型
```sql
- id: 主键
- name: 模型名称
- task_id: 关联的训练任务ID
- task_type: 任务类型
- model_type: 模型规格 (yolo11n/s/m/l/x)
- weight_path: 权重文件路径
- config_path: 配置文件路径
- metrics: 评估指标（JSON）
- size: 文件大小
- created_at: 创建时间
```

### TrainingTask表 - 训练任务
```sql
- id: 主键
- name: 任务名称
- dataset_id: 关联的数据集ID
- model_type: 模型规格
- task_type: 任务类型
- epochs: 训练轮数
- batch_size: 批次大小
- img_size: 图像尺寸
- status: 状态 (pending/training/completed/failed/stopped)
- progress: 进度（0-100）
- current_epoch: 当前轮数
- logs: 训练日志
- output_path: 输出路径
- created_at: 创建时间
- started_at: 开始时间
- completed_at: 完成时间
```

## 使用流程

### 1. 准备数据集

**检测/分割数据集格式：**
```
dataset.zip
├── train/
│   ├── images/          # 训练图片
│   └── labels/          # YOLO格式标签
└── val/
    ├── images/          # 验证图片
    └── labels/          # YOLO格式标签
```

**分类数据集格式：**
```
dataset.zip
├── train/
│   ├── class1/          # 类别1图片
│   ├── class2/          # 类别2图片
│   └── ...
└── val/
    ├── class1/          # 类别1验证图片
    ├── class2/          # 类别2验证图片
    └── ...
```

### 2. 上传数据集
1. 进入"数据集管理"页面
2. 点击"上传数据集"
3. 填写名称、选择类型、添加描述
4. 选择ZIP文件
5. 上传并等待处理完成

### 3. 创建训练任务
1. 进入"模型训练"页面
2. 点击"创建训练任务"
3. 选择已上传的数据集
4. 配置参数：
   - 任务类型（自动匹配数据集）
   - 模型规格（n/s/m/l/x，越大越慢但越准确）
   - 训练轮数（推荐100-300）
   - 批次大小（根据GPU显存调整）
   - 图像尺寸（640是常用值）
5. 提交并等待训练开始

### 4. 监控训练
1. 在训练任务列表查看进度条
2. 点击"详情"查看详细信息
3. 可以查看训练日志
4. 必要时可以停止训练

### 5. 下载模型
1. 训练完成后进入"模型管理"
2. 找到对应的模型
3. 点击"下载"获取.pt文件
4. 可在本地使用Ultralytics库加载

## 性能优化建议

### GPU加速
安装CUDA版本的PyTorch可获得10-50倍加速：
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 参数调优
- **批次大小**：GPU显存允许的情况下尽量大
  - 8GB显存：batch_size=8-16
  - 16GB显存：batch_size=16-32
  
- **图像尺寸**：根据需求平衡速度和精度
  - 320: 最快，适合实时应用
  - 640: 平衡，推荐使用
  - 1280: 最准，适合精度要求高的场景

- **模型选择**：
  - yolo11n: 最快，适合边缘设备
  - yolo11s/m: 平衡选择
  - yolo11l/x: 最准确，需要强大GPU

## 常见问题

### Q1: 上传的数据集一直显示"处理中"？
A: 检查数据集格式是否正确，查看后端日志了解具体错误。

### Q2: 训练任务创建后没有开始？
A: 确保后端服务正在运行，检查数据集状态是否为"就绪"。

### Q3: 训练速度很慢？
A: 
- 检查是否使用GPU版本PyTorch
- 减小批次大小或图像尺寸
- 选择更小的模型规格

### Q4: 训练失败了怎么办？
A: 
- 查看任务详情中的日志
- 检查数据集格式是否正确
- 确保系统有足够的内存和磁盘空间

### Q5: 如何使用训练好的模型？
A: 
```python
from ultralytics import YOLO

# 加载模型
model = YOLO('path/to/downloaded/model.pt')

# 预测
results = model('image.jpg')

# 查看结果
results[0].show()
```

## 系统要求

### 最低配置
- CPU: 4核心
- 内存: 8GB
- 磁盘: 20GB可用空间
- 系统: Windows 10/11, Ubuntu 18.04+, macOS 10.14+

### 推荐配置
- CPU: 8核心+
- 内存: 16GB+
- GPU: NVIDIA GPU (8GB+ VRAM)
- 磁盘: 50GB+ SSD
- 系统: Windows 11, Ubuntu 20.04+

## 后续开发计划

- [ ] 数据增强配置
- [ ] 训练可视化图表（loss、mAP曲线）
- [ ] 模型评估功能
- [ ] 在线推理测试
- [ ] 用户权限管理
- [ ] 分布式训练支持
- [ ] 模型格式转换（ONNX、TensorRT）
- [ ] 训练队列管理
- [ ] 自动超参数调优

## 技术支持

如遇到问题：
1. 查看 `README.md` 和 `QUICK_START.md`
2. 检查后端控制台日志
3. 查看浏览器开发者工具的Network和Console
4. 提交Issue到项目仓库

## 许可证

本项目采用 MIT 许可证。

## 致谢

- YOLOv11: Ultralytics
- 前端框架: Vue.js
- UI组件: Ant Design Vue
- 后端框架: Flask
