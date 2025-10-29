# 数据集准备指南

本文档详细说明如何准备符合YOLOv11训练要求的数据集。

## 一、目标检测数据集

### 1. 目录结构

```
dataset/
├── data.yaml              # 配置文件（可选，系统会自动生成）
├── train/
│   ├── images/           # 训练图像
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── labels/           # 训练标签
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
└── val/
    ├── images/           # 验证图像
    │   ├── image1.jpg
    │   └── ...
    └── labels/           # 验证标签
        ├── image1.txt
        └── ...
```

### 2. 标签格式

每个图像对应一个同名的txt标签文件，格式为：

```
class_id center_x center_y width height
```

- `class_id`: 类别索引（从0开始）
- `center_x`: 边界框中心X坐标（归一化到0-1）
- `center_y`: 边界框中心Y坐标（归一化到0-1）
- `width`: 边界框宽度（归一化到0-1）
- `height`: 边界框高度（归一化到0-1）

示例（`image1.txt`）：
```
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2
```

### 3. data.yaml配置（可选）

```yaml
path: .
train: train/images
val: val/images

nc: 2  # 类别数量
names: ['class0', 'class1']  # 类别名称
```

### 4. 示例：人脸检测数据集

```
face_detection/
├── train/
│   ├── images/
│   │   ├── face_001.jpg
│   │   ├── face_002.jpg
│   │   └── ...
│   └── labels/
│       ├── face_001.txt    # 内容: 0 0.5 0.4 0.2 0.3
│       ├── face_002.txt
│       └── ...
└── val/
    ├── images/
    │   └── ...
    └── labels/
        └── ...
```

## 二、图像分类数据集

### 1. 目录结构

```
dataset/
├── train/
│   ├── class1/           # 第一个类别
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   ├── class2/           # 第二个类别
│   │   ├── img1.jpg
│   │   ├── img2.jpg
│   │   └── ...
│   └── class3/           # 第三个类别
│       └── ...
└── val/
    ├── class1/
    │   └── ...
    ├── class2/
    │   └── ...
    └── class3/
        └── ...
```

### 2. 说明

- 每个子文件夹代表一个类别
- 文件夹名称即为类别名称
- 图像直接放在对应类别的文件夹中

### 3. 示例：动物分类数据集

```
animal_classification/
├── train/
│   ├── cat/
│   │   ├── cat_001.jpg
│   │   ├── cat_002.jpg
│   │   └── ...
│   ├── dog/
│   │   ├── dog_001.jpg
│   │   ├── dog_002.jpg
│   │   └── ...
│   └── bird/
│       ├── bird_001.jpg
│       └── ...
└── val/
    ├── cat/
    ├── dog/
    └── bird/
```

## 三、图像分割数据集

### 1. 目录结构

```
dataset/
├── data.yaml              # 配置文件（可选）
├── train/
│   ├── images/           # 训练图像
│   │   ├── image1.jpg
│   │   └── ...
│   └── labels/           # 训练标签
│       ├── image1.txt
│       └── ...
└── val/
    ├── images/           # 验证图像
    └── labels/           # 验证标签
```

### 2. 标签格式

每个图像对应一个同名的txt标签文件，格式为：

```
class_id x1 y1 x2 y2 x3 y3 ...
```

- `class_id`: 类别索引（从0开始）
- `x1 y1 x2 y2 ...`: 分割多边形的顶点坐标（归一化到0-1）

示例（`image1.txt`）：
```
0 0.1 0.1 0.2 0.1 0.2 0.2 0.1 0.2
1 0.5 0.5 0.6 0.5 0.6 0.6 0.5 0.6
```

## 四、数据集打包

### 1. 压缩为ZIP

准备好数据集后，将整个数据集文件夹压缩为ZIP格式：

**Windows：**
- 右键点击数据集文件夹
- 选择"发送到" -> "压缩(zipped)文件夹"

**Linux/Mac：**
```bash
zip -r dataset.zip dataset/
```

### 2. 注意事项

- ✅ 确保ZIP文件内包含正确的目录结构
- ✅ 图像格式支持：.jpg, .jpeg, .png
- ✅ 标签文件必须是UTF-8编码的txt文件
- ✅ 训练集和验证集都必须存在
- ❌ 不要在ZIP内包含额外的嵌套文件夹
- ❌ 不要包含.DS_Store等系统隐藏文件

## 五、数据标注工具推荐

### 目标检测标注工具

1. **LabelImg**
   - 链接: https://github.com/heartexlabs/labelImg
   - 特点: 简单易用，直接生成YOLO格式
   - 适合: 个人使用，小规模数据集

2. **CVAT**
   - 链接: https://github.com/opencv/cvat
   - 特点: 功能强大，支持团队协作
   - 适合: 大规模数据集，团队项目

3. **Label Studio**
   - 链接: https://labelstud.io/
   - 特点: 支持多种标注类型
   - 适合: 多任务标注需求

### 图像分割标注工具

1. **Labelme**
   - 链接: https://github.com/wkentaro/labelme
   - 特点: 支持多边形标注
   - 适合: 实例分割标注

2. **CVAT**
   - 也支持分割标注

### 图像分类

- 直接通过文件管理器手动分类到不同文件夹即可

## 六、数据集质量检查清单

上传前请确认：

- [ ] 图像和标签数量匹配
- [ ] 标签文件格式正确
- [ ] 坐标值在0-1范围内
- [ ] 类别ID从0开始连续编号
- [ ] 训练集和验证集比例合理（推荐8:2或7:3）
- [ ] 图像质量良好，无损坏文件
- [ ] 标签准确，边界框位置正确
- [ ] ZIP文件大小在系统限制内（默认500MB）

## 七、示例数据集下载

### 公开数据集

1. **COCO数据集** (目标检测)
   - 官网: https://cocodataset.org/
   - 需要转换为YOLO格式

2. **ImageNet** (图像分类)
   - 官网: https://www.image-net.org/

3. **Pascal VOC** (检测+分割)
   - 官网: http://host.robots.ox.ac.uk/pascal/VOC/

### YOLO格式数据集

Ultralytics提供了一些预处理好的数据集：

```python
from ultralytics import YOLO

# 使用内置数据集
model = YOLO('yolo11n.pt')
model.train(data='coco128.yaml')  # COCO的128张图片子集
```

## 八、快速测试数据集

创建最小测试数据集（10张图片）：

```
test_dataset/
├── train/
│   ├── images/
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   └── ... (共8张)
│   └── labels/
│       ├── 1.txt
│       ├── 2.txt
│       └── ... (共8个)
└── val/
    ├── images/
    │   ├── 9.jpg
    │   └── 10.jpg
    └── labels/
        ├── 9.txt
        └── 10.txt
```

用这个小数据集测试平台功能：
- 上传速度快
- 训练速度快（设置epochs=5）
- 可以快速验证流程

## 九、常见错误及解决方案

### 错误1: "标签文件缺失"

**原因**: 某些图像没有对应的标签文件

**解决**: 
```bash
# 检查是否所有图像都有标签
cd train/images && ls *.jpg | sed 's/.jpg//' > /tmp/images.txt
cd ../labels && ls *.txt | sed 's/.txt//' > /tmp/labels.txt
diff /tmp/images.txt /tmp/labels.txt
```

### 错误2: "标签格式错误"

**原因**: 标签文件中的数值格式不正确

**解决**: 确保：
- 每行有5个数值（检测）
- 所有数值在0-1之间
- 使用空格分隔
- 类别ID是整数

### 错误3: "数据集目录结构错误"

**原因**: 缺少必要的文件夹

**解决**: 确保包含以下路径：
```
train/images/
train/labels/
val/images/
val/labels/
```

## 十、性能优化建议

### 数据集大小

- **小数据集** (< 1000张): 增加数据增强
- **中等数据集** (1000-10000张): 标准配置
- **大数据集** (> 10000张): 可以获得最佳效果

### 图像质量

- 分辨率: 建议至少640x640
- 格式: JPEG (节省空间) 或 PNG (无损)
- 质量: 避免过度压缩

### 标注质量

- 边界框要紧贴目标
- 避免遗漏小目标
- 类别标签要准确
- 检查并修正错误标注

---

准备好数据集后，打包成ZIP文件，在平台的"数据集管理"页面上传即可开始训练！
