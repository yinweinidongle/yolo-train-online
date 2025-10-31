"""
Database Migration Script: Fix Model Config Paths

This script updates existing model records to include the correct config_path
so that training result images can be displayed.

Run this script if you have models that were created before the config_path
feature was added.
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, Model, TrainingTask

def fix_model_paths():
    """Fix config_path for existing models"""
    with app.app_context():
        # Get all models
        models = Model.query.all()
        updated_count = 0
        
        for model in models:
            if model.task_id and not model.config_path:
                # Find the corresponding training task
                task = TrainingTask.query.filter_by(id=model.task_id).first()
                
                if task and task.output_path and os.path.exists(task.output_path):
                    # Update model with the training output path
                    model.config_path = task.output_path
                    print(f"✓ Updated Model {model.id} ({model.name})")
                    print(f"  config_path: {task.output_path}")
                    updated_count += 1
                else:
                    # Try to infer from runs directory
                    runs_dir = os.path.join(os.path.dirname(__file__), 'runs')
                    task_dir = os.path.join(runs_dir, f'task_{model.task_id}')
                    
                    if os.path.exists(task_dir):
                        model.config_path = task_dir
                        print(f"✓ Updated Model {model.id} ({model.name})")
                        print(f"  config_path (inferred): {task_dir}")
                        updated_count += 1
                        
                        # Also update the task if it exists
                        if task and not task.output_path:
                            task.output_path = task_dir
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully updated {updated_count} model(s)!")
        else:
            print("\nℹ No models needed updating.")
        
        # Verification
        print("\n=== Verification ===")
        models = Model.query.all()
        for m in models:
            has_images = False
            if m.config_path:
                results_file = os.path.join(m.config_path, 'train', 'results.png')
                has_images = os.path.exists(results_file)
            
            status = "✓ Has images" if has_images else "✗ No images"
            print(f"Model {m.id}: {m.name} - {status}")

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Fix Model Config Paths")
    print("=" * 60)
    fix_model_paths()
    print("\n" + "=" * 60)
    print("Migration completed!")
    print("=" * 60)
