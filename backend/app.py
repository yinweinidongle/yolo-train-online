from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, Dataset, Model, TrainingTask
from train_service import TrainingService
import json

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
    
    return send_file(model.weight_path, as_attachment=True)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
