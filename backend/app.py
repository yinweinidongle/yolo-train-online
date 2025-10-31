from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, Dataset, Model, TrainingTask
from train_service import TrainingService
import json
import cv2
import numpy as np
from ultralytics import YOLO
import base64

app = Flask(__name__)
CORS(app)

# 配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "yolo_platform.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# 创建必要的目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'datasets'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'models'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'runs'), exist_ok=True)

# 初始化数据库
db.init_app(app)

with app.app_context():
    db.create_all()

# 训练服务
training_service = TrainingService(
    datasets_dir=os.path.join(BASE_DIR, 'datasets'),
    models_dir=os.path.join(BASE_DIR, 'models'),
    runs_dir=os.path.join(BASE_DIR, 'runs')
)

# ==================== 数据集管理 API ====================

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """获取所有数据集"""
    datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'data': [d.to_dict() for d in datasets],
        'message': '获取成功'
    })

@app.route('/api/datasets/<int:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """获取单个数据集详情"""
    dataset = Dataset.query.get_or_404(dataset_id)
    return jsonify({
        'code': 200,
        'data': dataset.to_dict(),
        'message': '获取成功'
    })

@app.route('/api/datasets/upload', methods=['POST'])
def upload_dataset():
    """上传数据集"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    name = request.form.get('name')
    task_type = request.form.get('task_type', 'detect')
    description = request.form.get('description', '')
    
    if not file or not name:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    if file.filename == '':
        return jsonify({'code': 400, 'message': '文件名为空'}), 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{timestamp}_{filename}')
        file.save(upload_path)
        
        # 解压并处理数据集
        dataset_path = training_service.process_dataset(upload_path, name, task_type)
        
        # 获取数据集统计信息
        stats = training_service.get_dataset_stats(dataset_path)
        
        # 创建数据集记录
        dataset = Dataset(
            name=name,
            task_type=task_type,
            description=description,
            path=dataset_path,
            file_count=stats.get('total_images', 0),
            size=os.path.getsize(upload_path),
            format='zip',
            status='ready'
        )
        db.session.add(dataset)
        db.session.commit()
        
        # 清理上传文件
        os.remove(upload_path)
        
        return jsonify({
            'code': 200,
            'data': dataset.to_dict(),
            'message': '数据集上传成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'上传失败: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除数据集"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        # 删除文件
        if os.path.exists(dataset.path):
            import shutil
            shutil.rmtree(dataset.path)
        
        # 删除数据库记录
        db.session.delete(dataset)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '数据集删除成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>/download', methods=['GET'])
def download_dataset(dataset_id):
    """下载数据集"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if not dataset.path or not os.path.exists(dataset.path):
        return jsonify({'code': 404, 'message': '数据集文件不存在'}), 404
    
    try:
        import shutil
        import tempfile
        
        # 创建临时zip文件
        temp_dir = tempfile.gettempdir()
        zip_filename = f"{dataset.name}_{dataset_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        # 压缩数据集目录
        shutil.make_archive(
            zip_path.replace('.zip', ''),
            'zip',
            dataset.path
        )
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'code': 500, 'message': f'下载失败: {str(e)}'}), 500

# ==================== 模型管理 API ====================

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取所有模型"""
    models = Model.query.order_by(Model.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'data': [m.to_dict() for m in models],
        'message': '获取成功'
    })

@app.route('/api/models/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """获取模型详情"""
    model = Model.query.get_or_404(model_id)
    return jsonify({
        'code': 200,
        'data': model.to_dict(),
        'message': '获取成功'
    })

@app.route('/api/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """删除模型"""
    model = Model.query.get_or_404(model_id)
    
    try:
        # 删除模型文件
        if model.weight_path and os.path.exists(model.weight_path):
            os.remove(model.weight_path)
        
        # 删除数据库记录
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '模型删除成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/models/<int:model_id>/download', methods=['GET'])
def download_model(model_id):
    """下载模型"""
    model = Model.query.get_or_404(model_id)
    
    if not model.weight_path or not os.path.exists(model.weight_path):
        return jsonify({'code': 404, 'message': '模型文件不存在'}), 404
    
    # 获取文件名
    filename = os.path.basename(model.weight_path)
    
    return send_file(
        model.weight_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

@app.route('/api/models/<int:model_id>/training-images', methods=['GET'])
def get_training_images(model_id):
    """获取模型训练结果图片列表"""
    model = Model.query.get_or_404(model_id)
    
    print(f"DEBUG: Getting training images for model {model_id}")
    print(f"DEBUG: config_path = {model.config_path}")
    
    images = []
    
    # 从 metrics中获取图片路径，或从 config_path 查找
    if model.config_path and os.path.exists(model.config_path):
        train_dir = os.path.join(model.config_path, 'train')
        print(f"DEBUG: train_dir = {train_dir}")
        print(f"DEBUG: train_dir exists = {os.path.exists(train_dir)}")
        
        if os.path.exists(train_dir):
            # 常见的训练结果图片
            image_files = [
                'results.png',
                'confusion_matrix.png',
                'confusion_matrix_normalized.png',
                'F1_curve.png',
                'P_curve.png',
                'R_curve.png',
                'PR_curve.png'
            ]
            
            for img_file in image_files:
                img_path = os.path.join(train_dir, img_file)
                if os.path.exists(img_path):
                    images.append({
                        'name': img_file,
                        'url': f'/models/{model_id}/training-images/{img_file}'
                    })
                    print(f"DEBUG: Found image: {img_file}")
    
    print(f"DEBUG: Total images found: {len(images)}")
    
    return jsonify({
        'code': 200,
        'data': images,
        'message': '获取成功'
    })

@app.route('/api/models/<int:model_id>/training-images/<path:filename>', methods=['GET'])
def get_training_image(model_id, filename):
    """获取具体的训练图片"""
    model = Model.query.get_or_404(model_id)
    
    if not model.config_path:
        return jsonify({'code': 404, 'message': '训练结果不存在'}), 404
    
    img_path = os.path.join(model.config_path, 'train', filename)
    
    if not os.path.exists(img_path):
        return jsonify({'code': 404, 'message': '图片不存在'}), 404
    
    return send_file(img_path, mimetype='image/png')

# ==================== 训练任务 API ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有训练任务"""
    tasks = TrainingTask.query.order_by(TrainingTask.created_at.desc()).all()
    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in tasks],
        'message': '获取成功'
    })

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取训练任务详情"""
    task = TrainingTask.query.get_or_404(task_id)
    return jsonify({
        'code': 200,
        'data': task.to_dict(),
        'message': '获取成功'
    })

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """创建训练任务"""
    data = request.json
    
    dataset_id = data.get('dataset_id')
    task_name = data.get('task_name')
    model_type = data.get('model_type', 'yolo11n')
    epochs = data.get('epochs', 100)
    batch_size = data.get('batch_size', 16)
    img_size = data.get('img_size', 640)
    task_type = data.get('task_type', 'detect')
    
    if not dataset_id or not task_name:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({'code': 404, 'message': '数据集不存在'}), 404
    
    try:
        # 创建训练任务记录
        task = TrainingTask(
            name=task_name,
            dataset_id=dataset_id,
            model_type=model_type,
            task_type=task_type,
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        # 启动训练（异步）
        training_service.start_training(
            task_id=task.id,
            dataset_path=dataset.path,
            task_type=task_type,
            model_type=model_type,
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size
        )
        
        return jsonify({
            'code': 200,
            'data': task.to_dict(),
            'message': '训练任务创建成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500

@app.route('/api/tasks/<int:task_id>/stop', methods=['POST'])
def stop_task(task_id):
    """停止训练任务"""
    task = TrainingTask.query.get_or_404(task_id)
    
    try:
        training_service.stop_training(task_id)
        
        task.status = 'stopped'
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '任务已停止'
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'停止失败: {str(e)}'}), 500

@app.route('/api/tasks/<int:task_id>/progress', methods=['GET'])
def get_task_progress(task_id):
    """获取训练进度"""
    task = TrainingTask.query.get_or_404(task_id)
    progress = training_service.get_training_progress(task_id)
    
    return jsonify({
        'code': 200,
        'data': {
            'task': task.to_dict(),
            'progress': progress
        },
        'message': '获取成功'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    dataset_count = Dataset.query.count()
    model_count = Model.query.count()
    task_count = TrainingTask.query.count()
    training_count = TrainingTask.query.filter_by(status='training').count()
    
    return jsonify({
        'code': 200,
        'data': {
            'dataset_count': dataset_count,
            'model_count': model_count,
            'task_count': task_count,
            'training_count': training_count
        },
        'message': '获取成功'
    })

# ==================== 模型推理 API ====================

@app.route('/api/inference/predict', methods=['POST'])
def predict():
    """模型推理/验证"""
    if 'image' not in request.files:
        return jsonify({'code': 400, 'message': '没有上传图片'}), 400
    
    image_file = request.files['image']
    model_id = request.form.get('model_id')
    confidence = float(request.form.get('confidence', 0.25))
    iou = float(request.form.get('iou', 0.45))
    
    if not model_id:
        return jsonify({'code': 400, 'message': '缺少模型 ID'}), 400
    
    try:
        # 获取模型
        model = Model.query.get(model_id)
        if not model:
            return jsonify({'code': 404, 'message': '模型不存在'}), 404
        
        if not model.weight_path or not os.path.exists(model.weight_path):
            return jsonify({'code': 404, 'message': '模型文件不存在'}), 404
        
        # 读取图片
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'code': 400, 'message': '无效的图片文件'}), 400
        
        # 加载模型
        yolo_model = YOLO(model.weight_path)
        
        # 执行推理
        import time
        start_time = time.time()
        results = yolo_model.predict(
            img,
            conf=confidence,
            iou=iou,
            verbose=False
        )
        inference_time = int((time.time() - start_time) * 1000)
        
        # 解析结果
        result = results[0]
        detections = []
        
        # 处理不同任务类型
        task_type = model.task_type
        
        if task_type == 'classify':
            # 分类任务
            if hasattr(result, 'probs') and result.probs is not None:
                probs = result.probs.data.cpu().numpy()
                top5_idx = probs.argsort()[::-1][:5]
                
                for idx in top5_idx:
                    detections.append({
                        'class': result.names[idx],
                        'confidence': float(probs[idx]),
                        'bbox': None
                    })
                
                # 绘制结果（分类任务只显示原图+文字）
                annotated_img = img.copy()
                # 添加文字标注
                top_class = result.names[top5_idx[0]]
                top_conf = float(probs[top5_idx[0]])
                cv2.putText(annotated_img, f'{top_class}: {top_conf:.2f}', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                annotated_img = img
        
        elif task_type in ['detect', 'segment']:
            # 检测/分割任务
            annotated_img = result.plot()
            
            # 提取检测信息
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = result.names[cls]
                    
                    detections.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': bbox
                    })
        else:
            # 未知任务类型，使用默认处理
            annotated_img = result.plot()
        
        # 将结果图片转为base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        img_data_url = f'data:image/jpeg;base64,{img_base64}'
        
        return jsonify({
            'code': 200,
            'data': {
                'image': img_data_url,
                'detections': detections,
                'inference_time': inference_time,
                'task_type': task_type
            },
            'message': '识别成功'
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Inference error: {str(e)}")
        print(error_trace)
        return jsonify({'code': 500, 'message': f'识别失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
