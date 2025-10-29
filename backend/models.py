from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Dataset(db.Model):
    """数据集模型"""
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # detect, classify, segment
    description = db.Column(db.Text)
    path = db.Column(db.String(500), nullable=False)
    file_count = db.Column(db.Integer, default=0)
    size = db.Column(db.BigInteger, default=0)  # bytes
    format = db.Column(db.String(50), default='zip')
    status = db.Column(db.String(50), default='processing')  # processing, ready, error
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    training_tasks = db.relationship('TrainingTask', backref='dataset', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'task_type': self.task_type,
            'description': self.description,
            'path': self.path,
            'file_count': self.file_count,
            'size': self.size,
            'format': self.format,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Model(db.Model):
    """模型模型"""
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('training_tasks.id'))
    task_type = db.Column(db.String(50), nullable=False)  # detect, classify, segment
    model_type = db.Column(db.String(50), nullable=False)  # yolo11n, yolo11s, etc.
    weight_path = db.Column(db.String(500))
    config_path = db.Column(db.String(500))
    metrics = db.Column(db.Text)  # JSON string
    size = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        metrics_data = {}
        if self.metrics:
            try:
                metrics_data = json.loads(self.metrics)
            except:
                pass
        
        return {
            'id': self.id,
            'name': self.name,
            'task_id': self.task_id,
            'task_type': self.task_type,
            'model_type': self.model_type,
            'weight_path': self.weight_path,
            'config_path': self.config_path,
            'metrics': metrics_data,
            'size': self.size,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class TrainingTask(db.Model):
    """训练任务模型"""
    __tablename__ = 'training_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # yolo11n, yolo11s, yolo11m, yolo11l, yolo11x
    task_type = db.Column(db.String(50), nullable=False)  # detect, classify, segment
    epochs = db.Column(db.Integer, default=100)
    batch_size = db.Column(db.Integer, default=16)
    img_size = db.Column(db.Integer, default=640)
    status = db.Column(db.String(50), default='pending')  # pending, training, completed, failed, stopped
    progress = db.Column(db.Float, default=0.0)
    current_epoch = db.Column(db.Integer, default=0)
    logs = db.Column(db.Text)
    output_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # 关联关系
    models = db.relationship('Model', backref='training_task', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dataset_id': self.dataset_id,
            'dataset_name': self.dataset.name if self.dataset else None,
            'model_type': self.model_type,
            'task_type': self.task_type,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'img_size': self.img_size,
            'status': self.status,
            'progress': self.progress,
            'current_epoch': self.current_epoch,
            'logs': self.logs,
            'output_path': self.output_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None
        }
