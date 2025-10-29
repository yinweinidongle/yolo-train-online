# YOLOv11在线训练平台 - 更新日志

## [1.0.0] - 2024-10-29

### 🎉 首次发布

完整的YOLOv11在线训练管理平台，支持目标检测、图像分类和图像分割任务。

### ✨ 新增功能

#### 数据集管理
- ✅ ZIP格式数据集上传
- ✅ 自动解析数据集结构
- ✅ 自动生成data.yaml配置
- ✅ 数据集统计信息展示
- ✅ 支持检测、分类、分割三种任务类型
- ✅ 数据集列表查看
- ✅ 数据集删除功能

#### 模型训练
- ✅ YOLOv11n/s/m/l/x 五种模型规格
- ✅ 灵活的训练参数配置
  - 训练轮数 (1-1000)
  - 批次大小 (1-128)
  - 图像尺寸 (320/416/640/1280)
- ✅ 异步后台训练
- ✅ 实时训练进度显示
- ✅ 训练日志记录
- ✅ 训练任务停止功能
- ✅ 训练任务列表管理

#### 模型管理
- ✅ 训练完成模型自动保存
- ✅ 模型列表查看
- ✅ 模型详情展示
- ✅ 模型文件下载
- ✅ 模型删除功能
- ✅ 训练参数记录

#### 用户界面
- ✅ 响应式布局设计
- ✅ 中文界面
- ✅ 仪表盘概览
- ✅ 统计信息展示
- ✅ 最近数据集和任务展示
- ✅ 快速操作入口
- ✅ 实时刷新功能

#### 技术特性
- ✅ Vue3 + Composition API
- ✅ Ant Design Vue 4.x
- ✅ Flask RESTful API
- ✅ SQLite数据库
- ✅ 文件上传进度显示
- ✅ 异步训练处理
- ✅ 自动训练回调
- ✅ 错误处理和提示

### 📦 项目结构

```
yolo-online/
├── backend/               # Python后端
│   ├── app.py            # Flask应用
│   ├── models.py         # 数据库模型
│   ├── train_service.py  # 训练服务
│   └── requirements.txt  # Python依赖
├── frontend/             # Vue3前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── layouts/     # 布局组件
│   │   ├── api/         # API接口
│   │   └── router/      # 路由配置
│   └── package.json     # 前端依赖
├── README.md            # 项目文档
├── QUICK_START.md       # 快速启动指南
├── DATASET_GUIDE.md     # 数据集准备指南
├── PROJECT_INFO.md      # 项目详细说明
├── start.bat            # Windows启动脚本
└── start.sh             # Linux/Mac启动脚本
```

### 🛠️ 技术栈

**前端**
- Vue 3.4.0
- Ant Design Vue 4.1.0
- Vue Router 4.2.5
- Pinia 2.1.7
- Axios 1.6.2
- Vite 5.0.0

**后端**
- Python 3.8+
- Flask 3.0.0
- SQLAlchemy
- Ultralytics YOLOv11
- PyTorch 2.0+

### 📝 API接口

#### 统计接口
- `GET /api/stats` - 获取平台统计信息

#### 数据集接口
- `GET /api/datasets` - 获取所有数据集
- `GET /api/datasets/<id>` - 获取数据集详情
- `POST /api/datasets/upload` - 上传数据集
- `DELETE /api/datasets/<id>` - 删除数据集

#### 模型接口
- `GET /api/models` - 获取所有模型
- `GET /api/models/<id>` - 获取模型详情
- `GET /api/models/<id>/download` - 下载模型
- `DELETE /api/models/<id>` - 删除模型

#### 训练任务接口
- `GET /api/tasks` - 获取所有训练任务
- `GET /api/tasks/<id>` - 获取任务详情
- `POST /api/tasks/create` - 创建训练任务
- `POST /api/tasks/<id>/stop` - 停止训练任务
- `GET /api/tasks/<id>/progress` - 获取训练进度

### 🔧 配置项

**后端配置 (app.py)**
- `SQLALCHEMY_DATABASE_URI`: 数据库连接
- `UPLOAD_FOLDER`: 上传目录
- `MAX_CONTENT_LENGTH`: 最大上传大小 (500MB)

**前端配置 (vite.config.js)**
- 开发服务器端口: 3000
- API代理: http://localhost:5000

### 📖 文档

- ✅ 完整的README文档
- ✅ 快速启动指南
- ✅ 数据集准备指南
- ✅ 项目详细说明
- ✅ API接口文档
- ✅ 代码注释

### 🚀 启动方式

**Windows:**
```bash
# 自动启动（推荐）
start.bat

# 手动启动
# 后端
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

# 前端
cd frontend
npm install
npm run dev
```

**Linux/Mac:**
```bash
# 自动启动
chmod +x start.sh
./start.sh

# 手动启动
# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# 前端
cd frontend
npm install
npm run dev
```

### 🔒 安全特性

- ✅ 文件名安全处理
- ✅ 文件大小限制
- ✅ 文件类型验证
- ✅ CORS跨域配置
- ✅ 错误处理和日志

### 🐛 已知问题

暂无

### 📋 待开发功能

- [ ] 数据增强配置界面
- [ ] 训练可视化图表
- [ ] 模型评估功能
- [ ] 在线推理测试
- [ ] 用户权限管理
- [ ] 分布式训练支持
- [ ] 模型格式转换
- [ ] 训练队列管理
- [ ] 自动超参数调优
- [ ] Docker部署支持

### 🙏 致谢

感谢以下开源项目：
- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics)
- [Vue.js](https://vuejs.org/)
- [Ant Design Vue](https://antdv.com/)
- [Flask](https://flask.palletsprojects.com/)

---

## 版本规划

### [1.1.0] - 计划中
- 数据增强配置
- 训练可视化图表
- 模型评估功能

### [1.2.0] - 计划中
- 在线推理测试
- 用户系统
- 权限管理

### [2.0.0] - 未来版本
- 分布式训练
- 模型转换
- 自动化调优

---

## 贡献指南

欢迎提交Issue和Pull Request！

### 报告Bug
请在Issue中包含：
1. 操作系统和版本
2. Python和Node.js版本
3. 详细的错误描述
4. 复现步骤
5. 相关日志

### 功能建议
请在Issue中描述：
1. 功能的使用场景
2. 期望的行为
3. 可能的实现方案

---

## 许可证

MIT License

Copyright (c) 2024 YOLOv11 Online Training Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
