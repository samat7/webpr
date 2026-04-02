from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate

class TaskService:
    @staticmethod
    def create_task(db: Session, user_id: int, task: TaskCreate) -> Task:
        db_task = Task(
            user_id=user_id,
            text=task.text,
            completed=task.completed
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        return db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
    
    @staticmethod
    def get_tasks_by_user(db: Session, user_id: int) -> List[Task]:
        return db.query(Task).filter(Task.user_id == user_id).all()
    
    @staticmethod
    def update_task(db: Session, task_id: int, user_id: int, task_update: TaskUpdate) -> Optional[Task]:
        db_task = TaskService.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        db_task = TaskService.get_task_by_id(db, task_id, user_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def delete_all_user_tasks(db: Session, user_id: int) -> int:
        deleted_count = db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        return deleted_count
    
    @staticmethod
    def get_task_stats(db: Session, user_id: int) -> dict:
        tasks = TaskService.get_tasks_by_user(db, user_id)
        total = len(tasks)
        completed = sum(1 for task in tasks if task.completed)
        active = total - completed
        
        return {
            "total": total,
            "completed": completed,
            "active": active
        }