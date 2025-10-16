import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    extracted_info = db.Column(db.Text, nullable=True)  # 存储AI提取的信息
    extracted_at = db.Column(db.DateTime, nullable=True)  # 信息提取时间
    translations = db.Column(db.Text, nullable=True)  # 以JSON格式存储多语言翻译结果
    translation_updated_at = db.Column(db.DateTime, nullable=True)  # 最近一次翻译更新时间
    quiz_question = db.Column(db.Text, nullable=True)  # 存储自动生成的题干
    quiz_options = db.Column(db.Text, nullable=True)  # 以JSON格式存储多项选择题选项
    quiz_answer = db.Column(db.String(50), nullable=True)  # 存储正确答案标识
    quiz_explanation = db.Column(db.Text, nullable=True)  # 存储答案解析
    quiz_generated_at = db.Column(db.DateTime, nullable=True)  # 最近一次题目生成时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def to_dict(self):
        """以字典形式对外输出笔记数据，便于前端直接消费"""
        try:
            translation_data = json.loads(self.translations) if self.translations else {}
        except json.JSONDecodeError:
            translation_data = {}

        try:
            quiz_options = json.loads(self.quiz_options) if self.quiz_options else []
        except json.JSONDecodeError:
            quiz_options = []

        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'extracted_info': self.extracted_info,
            'extracted_at': self.extracted_at.isoformat() if self.extracted_at else None,
            'translations': translation_data,
            'translation_updated_at': self.translation_updated_at.isoformat() if self.translation_updated_at else None,
            'quiz_question': self.quiz_question,
            'quiz_options': quiz_options,
            'quiz_answer': self.quiz_answer,
            'quiz_explanation': self.quiz_explanation,
            'quiz_generated_at': self.quiz_generated_at.isoformat() if self.quiz_generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

