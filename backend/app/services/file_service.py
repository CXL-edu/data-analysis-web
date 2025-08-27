"""
File upload service - SIMPLIFIED
"""
import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
from app.extensions import db
from database.models import UploadedFile
from app.utils.exceptions import ValidationError
from app.config import Config


class FileService:
    def is_allowed_file(self, filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    def upload_file(self, file, session_id, user_id):
        """Upload and save file"""
        if not self.is_allowed_file(file.filename):
            raise ValidationError('File type not allowed')
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Config.UPLOAD_FOLDER
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file to disk
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = file.content_type or 'application/octet-stream'
        
        # Create database record
        uploaded_file = UploadedFile(
            session_id=session_id,
            original_filename=original_filename,
            stored_filename=unique_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=mime_type
        )
        uploaded_file.save()
        
        return uploaded_file
    
    def get_file_preview(self, file_record, rows=5):
        """Get preview data for CSV/Excel files"""
        file_extension = file_record.original_filename.rsplit('.', 1)[1].lower()
        
        if file_extension not in ['csv', 'xlsx', 'xls']:
            raise ValidationError('Preview not available for this file type')
        
        if not os.path.exists(file_record.file_path):
            raise ValidationError('File not found on disk')
        
        try:
            # Read file based on extension
            if file_extension == 'csv':
                df = pd.read_csv(file_record.file_path, nrows=rows)
            else:  # xlsx or xls
                df = pd.read_excel(file_record.file_path, nrows=rows)
            
            # Convert to dictionary format
            preview_data = {
                'columns': df.columns.tolist(),
                'data': df.fillna('').values.tolist(),
                'stats': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'dtypes': df.dtypes.astype(str).to_dict()
                }
            }
            
            return preview_data
            
        except Exception as e:
            raise ValidationError(f'Could not read file: {str(e)}')