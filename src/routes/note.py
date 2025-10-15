from flask import Blueprint, jsonify, request
from src.models.note import Note, db
from datetime import datetime

note_bp = Blueprint('note', __name__)

@note_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, ordered by most recently updated"""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        
        note = Note(title=data['title'], content=data['content'])
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    notes = Note.query.filter(
        (Note.title.contains(query)) | (Note.content.contains(query))
    ).order_by(Note.updated_at.desc()).all()
    
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes/extract-info', methods=['POST'])
def extract_information():
    """Extract key information from note content using GitHub AI API"""
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': '文档内容不能为空'}), 400
        
        content = data['content'].strip()
        note_id = data.get('note_id')
        
        if not content:
            return jsonify({'error': '文档内容不能为空'}), 400
        
        # 如果提供了note_id，验证笔记是否存在
        if note_id:
            note = Note.query.get(note_id)
            if not note:
                return jsonify({'error': '笔记不存在'}), 404
        
        # Import here to avoid circular imports
        from src.services.ai_service import extract_key_info
        
        # Extract key information using GitHub AI API
        extracted_info = extract_key_info(content)
        
        # 如果提供了note_id，保存提取的信息到数据库
        if note_id and note:
            note.extracted_info = extracted_info
            note.extracted_at = datetime.utcnow()
            try:
                db.session.commit()
            except Exception as db_e:
                # 打印数据库提交错误与回溯，便于 Vercel 日志排查
                import traceback as _tb
                print('Exception committing extracted info to DB:', str(db_e))
                _tb.print_exc()
                db.session.rollback()
                return jsonify({'error': '保存提取信息失败', 'detail': str(db_e)}), 500
        
        return jsonify({
            'success': True,
            'extracted_info': extracted_info,
            'saved': bool(note_id)  # 指示是否已保存到数据库
        })
        
    except Exception as e:
        # 捕获并打印完整回溯，便于在 Vercel 日志中查看根因
        import traceback as _tb
        print('Exception in /api/notes/extract-info:', str(e))
        _tb.print_exc()
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': f'信息提取失败: {str(e)}'}), 500

