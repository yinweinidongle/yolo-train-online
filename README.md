# YOLOv11在线训练平台

基于Vue3 + Ant Design + Flask + YOLOv11的在线图像检测/分类/分割模型训练管理平台。

## 功能特性

✨ **数据集管理**
- 📤 支持上传ZIP格式数据集
- 📊 自动解析数据集结构
- 🏷️ 支持检测、分类、分割三种任务类型
- 📁 数据集列表查看与删除

✨ **模型训练**
- 🎯 支持YOLOv11n/s/m/l/x多种模型规格
- ⚙️ 灵活配置训练参数（轮数、批次大小、图像尺寸）
- 📈 实时查看训练进度
- 🛑 支持中途停止训练
- 📝 训练日志记录

✨ **模型管理**
- 💾 自动保存训练完成的模型
- 📥 模型下载功能
- 📊 模型详情查看
- 🗑️ 模型删除管理

## 技术栈

### 前端
- Vue 3.4
- Ant Design Vue 4.x
- Vue Router 4.x
- Pinia 2.x
- Axios
- ECharts
- Vite 5.x

### 后端
- Python 3.8+
- Flask 3.0
- SQLite
- YOLOv11 (Ultralytics)
- PyTorch

## 项目结构

```
yolo-online/
├── backend/                    # 后端目录
│   ├── app.py                 # Flask应用主文件
│   ├── models.py              # 数据库模型
│   ├── train_service.py       # 训练服务
│   ├── requirements.txt       # Python依赖
│   ├── datasets/              # 数据集存储目录
│   ├── models/                # 模型存储目录
│   ├── runs/                  # 训练输出目录
│   └── uploads/               # 临时上传目录
│
└── frontend/                   # 前端目录
    ├── src/
    │   ├── views/             # 页面组件
    │   │   ├── Dashboard.vue  # 仪表盘
    │   │   ├── Datasets.vue   # 数据集管理
    │   │   ├── Training.vue   # 模型训练
    │   │   └── Models.vue     # 模型管理
    │   ├── layouts/           # 布局组件
    │   ├── api/               # API接口
    │   ├── router/            # 路由配置
    │   └── utils/             # 工具函数
    ├── package.json
    └── vite.config.js
```

## 安装说明

### 1. 克隆项目

```bash
cd yolo-online
```

### 2. 后端安装

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 前端安装

```bash
cd frontend

# 安装依赖
npm install
```

## 运行项目

### 1. 启动后端

```bash
cd backend
python app.py
```

后端服务将运行在：`http://localhost:5000`

### 2. 启动前端

```bash
cd frontend
npm run dev
```

前端服务将运行在：`http://localhost:3000`

### 3. 访问应用

在浏览器中打开：`http://localhost:3000`

## 数据集格式说明

### 目标检测 / 图像分割

数据集应包含以下结构：

```
dataset.zip
├── data.yaml              # 配置文件（可选，系统会自动生成）
├── train/
│   ├── images/           # 训练图像
│   └── labels/           # 训练标签（YOLO格式）
└── val/
    ├── images/           # 验证图像
    └── labels/           # 验证标签
```

### 图像分类

数据集应包含以下结构：

```
dataset.zip
├── train/
│   ├── class1/           # 类别1的图像
│   ├── class2/           # 类别2的图像
│   └── ...
└── val/
    ├── class1/           # 类别1的验证图像
    ├── class2/           # 类别2的验证图像
    └── ...
```

## API接口文档

### 数据集相关

- `GET /api/datasets` - 获取所有数据集
- `GET /api/datasets/<id>` - 获取单个数据集
- `POST /api/datasets/upload` - 上传数据集
- `DELETE /api/datasets/<id>` - 删除数据集

### 模型相关

- `GET /api/models` - 获取所有模型
- `GET /api/models/<id>` - 获取模型详情
- `GET /api/models/<id>/download` - 下载模型
- `DELETE /api/models/<id>` - 删除模型

### 训练任务相关

- `GET /api/tasks` - 获取所有训练任务
- `GET /api/tasks/<id>` - 获取任务详情
- `POST /api/tasks/create` - 创建训练任务
- `POST /api/tasks/<id>/stop` - 停止训练任务
- `GET /api/tasks/<id>/progress` - 获取训练进度

### 统计信息

- `GET /api/stats` - 获取平台统计信息

## 使用说明

### 1. 上传数据集

1. 点击"数据集管理"菜单
2. 点击"上传数据集"按钮
3. 填写数据集名称、选择任务类型
4. 选择ZIP格式的数据集文件
5. 点击确定上传

### 2. 创建训练任务

1. 点击"模型训练"菜单
2. 点击"创建训练任务"按钮
3. 选择数据集
4. 配置训练参数：
   - 任务类型（检测/分类/分割）
   - 模型规格（n/s/m/l/x）
   - 训练轮数
   - 批次大小
   - 图像尺寸
5. 点击确定开始训练

### 3. 查看训练进度

1. 在训练任务列表中查看进度条
2. 点击"详情"按钮查看详细信息
3. 可以查看训练日志和当前状态

### 4. 下载模型

1. 训练完成后，在"模型管理"菜单中查看
2. 点击"下载"按钮下载训练好的模型
3. 下载的模型为PyTorch格式（.pt文件）

## 常见问题

### Q: 上传数据集失败？
A: 请检查：
1. 数据集格式是否正确
2. ZIP文件是否损坏
3. 文件大小是否超过限制（默认500MB）

### Q: 训练任务失败？
A: 请检查：
1. 数据集是否已准备就绪
2. 系统是否有足够的GPU/CPU资源
3. 查看训练日志了解具体错误

### Q: 如何使用训练好的模型？
A: 下载模型后，可以使用Ultralytics库加载：

```python
from ultralytics import YOLO

# 加载模型
model = YOLO('path/to/your/model.pt')

# 进行预测
results = model('path/to/image.jpg')
```

## 系统要求

- Python 3.8+
- Node.js 16+
- 8GB+ RAM（推荐16GB）
- NVIDIA GPU（推荐，CPU也可运行但速度较慢）
- 20GB+ 磁盘空间

## 开发计划

- [ ] 支持更多数据增强选项
- [ ] 添加训练可视化图表
- [ ] 支持模型评估和测试
- [ ] 添加用户权限管理
- [ ] 支持分布式训练
- [ ] 添加模型导出功能（ONNX、TensorRT等）

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请通过Issue联系我们。
