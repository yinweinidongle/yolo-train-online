import os
import shutil
import zipfile
import threading
import json
from datetime import datetime
from ultralytics import YOLO
import yaml
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
class TrainingService:
    def __init__(self, datasets_dir, models_dir, runs_dir):
        self.datasets_dir = datasets_dir
        self.models_dir = models_dir
        self.runs_dir = runs_dir
        self.training_threads = {}
        self.training_progress = {}
        
    def process_dataset(self, zip_path, name, task_type):
        """处理上传的数据集压缩包"""
        # 创建数据集目录
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        dataset_dir = os.path.join(self.datasets_dir, f"{timestamp}_{name}")
        os.makedirs(dataset_dir, exist_ok=True)
        
        # 解压文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dataset_dir)
        
        # 验证数据集结构并返回实际的数据集根目录
        actual_dataset_dir = self._validate_dataset_structure(dataset_dir, task_type)
        
        return actual_dataset_dir
    
    def _validate_dataset_structure(self, dataset_dir, task_type):
        """验证数据集结构"""
        # 查找实际的数据集根目录
        actual_dataset_dir = dataset_dir
        for root, dirs, files in os.walk(dataset_dir):
            if 'train' in dirs and 'val' in dirs:
                actual_dataset_dir = root
                break
        
        # 检查是否存在 data.yaml
        yaml_path = os.path.join(actual_dataset_dir, 'data.yaml')
        if not os.path.exists(yaml_path):
            # 自动生成 data.yaml
            actual_dataset_dir = self._generate_data_yaml(actual_dataset_dir, task_type)
        else:
            # 更新现有的data.yaml以修复路径
            actual_dataset_dir = self._generate_data_yaml(actual_dataset_dir, task_type)
        
        return actual_dataset_dir
    
    def _generate_data_yaml(self, dataset_dir, task_type):
        """自动生成 data.yaml 配置文件"""
        # 检查是否有嵌套的数据集目录
        actual_dataset_dir = dataset_dir
        
        # 查找实际的数据集根目录（包含train和val的目录）
        for root, dirs, files in os.walk(dataset_dir):
            if 'train' in dirs and 'val' in dirs:
                actual_dataset_dir = root
                break
        
        yaml_path = os.path.join(actual_dataset_dir, 'data.yaml')
        
        # 查找类别
        names = []
        if task_type == 'detect' or task_type == 'segment':
            # 从 labels 文件夹中推断类别
            train_labels = os.path.join(actual_dataset_dir, 'train', 'labels')
            if os.path.exists(train_labels):
                # 读取第一个标签文件获取类别信息
                label_files = [f for f in os.listdir(train_labels) if f.endswith('.txt')]
                if label_files:
                    # 简化处理：假设类别从0开始连续编号
                    max_class = -1
                    for label_file in label_files[:10]:  # 只检查前10个文件
                        label_path = os.path.join(train_labels, label_file)
                        try:
                            with open(label_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    parts = line.strip().split()
                                    if parts:
                                        max_class = max(max_class, int(parts[0]))
                        except:
                            pass
                    names = [f'class_{i}' for i in range(max_class + 1)]
        elif task_type == 'classify':
            # 从文件夹名称推断类别
            train_dir = os.path.join(actual_dataset_dir, 'train')
            if os.path.exists(train_dir):
                names = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
        
        if not names:
            names = ['class_0']  # 默认至少一个类别
        
        # 生成配置 - 使用绝对路径确保YOLO能找到数据
        # 将Windows路径转换为正斜杠，避免中文路径问题
        path_normalized = actual_dataset_dir.replace('\\', '/')
        
        data_config = {
            'path': path_normalized,
            'train': 'train/images' if task_type != 'classify' else 'train',
            'val': 'val/images' if task_type != 'classify' else 'val',
            'nc': len(names),
            'names': names
        }
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data_config, f, allow_unicode=True)
        
        return actual_dataset_dir
    
    def get_dataset_stats(self, dataset_path):
        """获取数据集统计信息"""
        stats = {'total_images': 0, 'train_images': 0, 'val_images': 0}
        
        # 统计训练集
        train_images = os.path.join(dataset_path, 'train', 'images')
        if os.path.exists(train_images):
            stats['train_images'] = len([f for f in os.listdir(train_images) 
                                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        else:
            train_dir = os.path.join(dataset_path, 'train')
            if os.path.exists(train_dir):
                for root, dirs, files in os.walk(train_dir):
                    stats['train_images'] += len([f for f in files 
                                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        # 统计验证集
        val_images = os.path.join(dataset_path, 'val', 'images')
        if os.path.exists(val_images):
            stats['val_images'] = len([f for f in os.listdir(val_images) 
                                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        else:
            val_dir = os.path.join(dataset_path, 'val')
            if os.path.exists(val_dir):
                for root, dirs, files in os.walk(val_dir):
                    stats['val_images'] += len([f for f in files 
                                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        
        stats['total_images'] = stats['train_images'] + stats['val_images']
        return stats
    
    def start_training(self, task_id, dataset_path, task_type, model_type, epochs, batch_size, img_size):
        """启动训练任务"""
        thread = threading.Thread(
            target=self._train_model,
            args=(task_id, dataset_path, task_type, model_type, epochs, batch_size, img_size)
        )
        thread.daemon = True
        self.training_threads[task_id] = thread
        self.training_progress[task_id] = {
            'status': 'starting',
            'progress': 0,
            'current_epoch': 0,
            'logs': []
        }
        thread.start()
    
    def _train_model(self, task_id, dataset_path, task_type, model_type, epochs, batch_size, img_size):
        """训练模型的实际逻辑"""
        import traceback
        from models import db, TrainingTask, Model
        from app import app
        
        with app.app_context():
            try:
                # 更新任务状态
                task = TrainingTask.query.get(task_id)
                if not task:
                    print(f"Error: Task {task_id} not found in database")
                    self.training_progress[task_id]['status'] = 'failed'
                    self.training_progress[task_id]['error'] = 'Task not found'
                    return
                
                print(f"Starting training for task {task_id}...")
                task.status = 'training'
                task.started_at = datetime.now()
                db.session.commit()
                
                self.training_progress[task_id]['status'] = 'training'
                
                # 验证数据集路径
                if not os.path.exists(dataset_path):
                    raise Exception(f"Dataset path does not exist: {dataset_path}")
                
                data_yaml = os.path.join(dataset_path, 'data.yaml')
                if not os.path.exists(data_yaml):
                    raise Exception(f"data.yaml not found at: {data_yaml}")
                
                # 对于分类任务，YOLO需要数据集目录路径（包含train/val子目录），而不是data.yaml文件路径
                # 对于检测/分割任务，YOLO需要data.yaml文件路径
                if task_type == 'classify':
                    # 分类任务：传递数据集目录路径
                    training_data_path = dataset_path.replace('\\', '/')
                    print(f"Classification task - using dataset directory: {training_data_path}")
                else:
                    # 检测/分割任务：传递data.yaml文件路径
                    training_data_path = data_yaml.replace('\\', '/')
                    print(f"Detection/Segmentation task - using data.yaml: {training_data_path}")
                
                print(f"Dataset path: {dataset_path}")
                print(f"data.yaml path: {data_yaml}")
                print(f"Training data path: {training_data_path}")
                
                # 选择模型
                model_map = {
                    'detect': f'{model_type}.pt',
                    'classify': f'{model_type}-cls.pt',
                    'segment': f'{model_type}-seg.pt'
                }
                model_file = model_map.get(task_type, f'{model_type}.pt')
                
                # 检查models目录中是否有预下载的模型
                local_model_path = os.path.join(self.models_dir, model_file)
                if os.path.exists(local_model_path):
                    model_path = local_model_path
                    print(f"Using local model: {model_path}")
                else:
                    model_path = model_file
                    print(f"Model will be downloaded: {model_file}")
                
                # 加载模型（处理下载错误）
                try:
                    model = YOLO(model_path)
                    print(f"Model loaded successfully!")
                except Exception as download_error:
                    # 如果GitHub下载失败，提供清晰的错误信息
                    error_msg = str(download_error)
                    if 'ProxyError' in error_msg or 'github.com' in error_msg:
                        raise Exception(
                            f"无法从GitHub下载模型文件 {model_file}。\n"
                            f"解决方案：\n"
                            f"1. 手动下载模型文件到 backend/models/ 目录：\n"
                            f"   - yolo11n.pt: https://github.com/ultralytics/assets/releases/download/v8.1.0/yolo11n.pt\n"
                            f"   - yolo11s.pt: https://github.com/ultralytics/assets/releases/download/v8.1.0/yolo11s.pt\n"
                            f"   - yolo11m.pt: https://github.com/ultralytics/assets/releases/download/v8.1.0/yolo11m.pt\n"
                            f"2. 或配置网络代理\n"
                            f"\n原始错误: {error_msg}"
                        )
                    else:
                        raise
                
                # 训练配置
                project_dir = os.path.join(self.runs_dir, f'task_{task_id}')
                print(f"Training output directory: {project_dir}")
                
                # 自定义回调函数
                def on_train_epoch_end(trainer):
                    try:
                        epoch = trainer.epoch + 1
                        progress = (epoch / epochs) * 100
                        
                        self.training_progress[task_id].update({
                            'progress': progress,
                            'current_epoch': epoch,
                            'logs': self.training_progress[task_id].get('logs', []) + 
                                   [f'Epoch {epoch}/{epochs} completed']
                        })
                        
                        # 更新数据库
                        task.progress = progress
                        task.current_epoch = epoch
                        db.session.commit()
                        print(f"Epoch {epoch}/{epochs} completed - Progress: {progress:.1f}%")
                    except Exception as e:
                        print(f"Error in epoch callback: {e}")
                
                # 添加回调
                model.add_callback('on_train_epoch_end', on_train_epoch_end)
                
                # 开始训练
                print(f"Starting YOLO training with: epochs={epochs}, batch={batch_size}, imgsz={img_size}")
                results = model.train(
                    data=training_data_path,
                    epochs=epochs,
                    batch=batch_size,
                    imgsz=img_size,
                    project=project_dir,
                    name='train',
                    exist_ok=True,
                    verbose=True
                )
                
                print("Training completed successfully!")
                
                # 训练完成，保存模型
                best_weights = os.path.join(project_dir, 'train', 'weights', 'best.pt')
                model_save_path = os.path.join(self.models_dir, f'task_{task_id}_best.pt')
                
                if os.path.exists(best_weights):
                    shutil.copy(best_weights, model_save_path)
                    print(f"Model saved to: {model_save_path}")
                    
                    # 获取训练结果图片路径
                    results_img = os.path.join(project_dir, 'train', 'results.png')
                    confusion_matrix = os.path.join(project_dir, 'train', 'confusion_matrix.png')
                    
                    # 创建模型记录
                    model_record = Model(
                        name=f'{task.name}_model',
                        task_id=task_id,
                        task_type=task_type,
                        model_type=model_type,
                        weight_path=model_save_path,
                        config_path=project_dir,  # 存储训练输出目录
                        size=os.path.getsize(model_save_path),
                        metrics=json.dumps({
                            'epochs': epochs,
                            'batch_size': batch_size,
                            'img_size': img_size,
                            'results_img': results_img if os.path.exists(results_img) else None,
                            'confusion_matrix': confusion_matrix if os.path.exists(confusion_matrix) else None
                        })
                    )
                    db.session.add(model_record)
                
                # 更新任务状态
                task.status = 'completed'
                task.progress = 100.0
                task.completed_at = datetime.now()
                task.output_path = project_dir
                db.session.commit()
                
                self.training_progress[task_id]['status'] = 'completed'
                print(f"Task {task_id} completed successfully!")
                
            except Exception as e:
                # 训练失败
                error_msg = str(e)
                error_trace = traceback.format_exc()
                print(f"Training failed for task {task_id}:")
                print(f"Error: {error_msg}")
                print(f"Traceback:\n{error_trace}")
                
                try:
                    task = TrainingTask.query.get(task_id)
                    if task:
                        task.status = 'failed'
                        task.logs = f"{error_msg}\n\n{error_trace}"
                        db.session.commit()
                except Exception as db_error:
                    print(f"Failed to update task status: {db_error}")
                
                self.training_progress[task_id]['status'] = 'failed'
                self.training_progress[task_id]['error'] = error_msg
                self.training_progress[task_id]['logs'] = self.training_progress[task_id].get('logs', []) + [f'Error: {error_msg}']
    
    def stop_training(self, task_id):
        """停止训练任务"""
        if task_id in self.training_threads:
            # 注意：线程不能直接停止，这里只是标记状态
            self.training_progress[task_id]['status'] = 'stopped'
            # 实际的停止需要在训练循环中检查状态
    
    def get_training_progress(self, task_id):
        """获取训练进度"""
        return self.training_progress.get(task_id, {
            'status': 'unknown',
            'progress': 0,
            'current_epoch': 0,
            'logs': []
        })
