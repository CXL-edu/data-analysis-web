"""
Data analysis service
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime
from flask import current_app
from app.extensions import db
from database.repositories.analysis_repository import AnalysisRepository
from database.models import UploadedFile
from app.utils.exceptions import NotFoundError, ValidationError
import os


class AnalysisService:
    def __init__(self):
        self.analysis_repo = AnalysisRepository()
    
    def perform_analysis(self, session_id, analysis_type, file_ids, parameters=None):
        """Perform data analysis on specified files"""
        if not file_ids:
            raise ValidationError('At least one file is required for analysis')
        
        # Load dataframes
        dataframes = self._load_dataframes(file_ids)
        if not dataframes:
            raise ValidationError('No valid data files found')
        
        # Perform analysis based on type
        result_data = self._execute_analysis(analysis_type, dataframes, parameters or {})
        
        # Save result to database
        return self.analysis_repo.create_result(
            session_id=session_id,
            analysis_type=analysis_type,
            result_data=result_data
        )
    
    def stream_analysis(self, session_id, analysis_type, file_ids, parameters=None):
        """Stream analysis results step by step"""
        if not file_ids:
            raise ValidationError('At least one file is required for analysis')
        
        # Load dataframes
        dataframes = self._load_dataframes(file_ids)
        if not dataframes:
            raise ValidationError('No valid data files found')
        
        # Stream analysis results
        yield from self._stream_analysis_steps(analysis_type, dataframes, parameters or {})
    
    def save_analysis_result(self, session_id, analysis_type, result_data):
        """Save analysis result to database"""
        return self.analysis_repo.create_result(
            session_id=session_id,
            analysis_type=analysis_type,
            result_data=result_data
        )
    
    def get_result_by_id(self, result_id):
        """Get analysis result by ID"""
        result = self.analysis_repo.find_by_id(result_id)
        if not result:
            raise NotFoundError('Analysis result not found')
        return result
    
    def delete_result(self, result_id):
        """Delete analysis result"""
        result = self.get_result_by_id(result_id)
        return self.analysis_repo.delete_result(result_id)
    
    def _load_dataframes(self, file_ids):
        """Load dataframes from file IDs"""
        dataframes = []
        for file_id in file_ids:
            try:
                file_record = UploadedFile.query.get(file_id)
                if not file_record or not os.path.exists(file_record.file_path):
                    continue
                
                df = self._load_single_dataframe(file_record)
                if df is not None:
                    dataframes.append({
                        'filename': file_record.original_filename,
                        'file_id': file_id,
                        'dataframe': df
                    })
            except Exception as e:
                current_app.logger.warning(f"Could not load file {file_id}: {e}")
        
        return dataframes
    
    def _load_single_dataframe(self, file_record):
        """Load a single dataframe from file record"""
        file_extension = file_record.original_filename.rsplit('.', 1)[1].lower()
        
        try:
            if file_extension == 'csv':
                return pd.read_csv(file_record.file_path)
            elif file_extension in ['xlsx', 'xls']:
                return pd.read_excel(file_record.file_path)
            else:
                return None
        except Exception as e:
            current_app.logger.error(f"Error loading {file_record.original_filename}: {e}")
            return None
    
    def _execute_analysis(self, analysis_type, dataframes, parameters):
        """Execute specific analysis type"""
        main_df = dataframes[0]['dataframe']
        
        if analysis_type == 'descriptive_stats':
            return self._descriptive_statistics(main_df)
        elif analysis_type == 'correlation_analysis':
            return self._correlation_analysis(main_df)
        elif analysis_type == 'data_profiling':
            return self._data_profiling(main_df)
        elif analysis_type == 'visualization':
            return self._visualization_analysis(main_df, parameters)
        elif analysis_type == 'anomaly_detection':
            return self._anomaly_detection(main_df)
        elif analysis_type == 'time_series':
            return self._time_series_analysis(main_df, parameters)
        else:
            raise ValidationError(f'Unknown analysis type: {analysis_type}')
    
    def _stream_analysis_steps(self, analysis_type, dataframes, parameters):
        """Stream analysis steps for real-time updates"""
        main_df = dataframes[0]['dataframe']
        
        if analysis_type == 'descriptive_stats':
            yield {'step': 'loading_data', 'progress': 10}
            yield {'step': 'calculating_stats', 'progress': 50}
            result = self._descriptive_statistics(main_df)
            yield {'step': 'complete', 'progress': 100, 'result': result}
            
        elif analysis_type == 'correlation_analysis':
            yield {'step': 'loading_data', 'progress': 10}
            yield {'step': 'calculating_correlations', 'progress': 60}
            result = self._correlation_analysis(main_df)
            yield {'step': 'complete', 'progress': 100, 'result': result}
            
        elif analysis_type == 'data_profiling':
            yield {'step': 'loading_data', 'progress': 10}
            yield {'step': 'profiling_columns', 'progress': 30}
            yield {'step': 'checking_quality', 'progress': 60}
            yield {'step': 'generating_summary', 'progress': 90}
            result = self._data_profiling(main_df)
            yield {'step': 'complete', 'progress': 100, 'result': result}
            
        else:
            # Default streaming for other types
            yield {'step': 'analyzing', 'progress': 50}
            result = self._execute_analysis(analysis_type, dataframes, parameters)
            yield {'step': 'complete', 'progress': 100, 'result': result}
    
    def _descriptive_statistics(self, df):
        """Calculate descriptive statistics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        stats = {
            'overview': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(numeric_cols),
                'categorical_columns': len(categorical_cols),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
            },
            'numeric_stats': {},
            'categorical_stats': {}
        }
        
        # Numeric statistics
        for col in numeric_cols:
            series = df[col].dropna()
            stats['numeric_stats'][col] = {
                'count': len(series),
                'mean': float(series.mean()),
                'median': float(series.median()),
                'std': float(series.std()),
                'min': float(series.min()),
                'max': float(series.max()),
                'quartile_25': float(series.quantile(0.25)),
                'quartile_75': float(series.quantile(0.75)),
                'skewness': float(series.skew()),
                'kurtosis': float(series.kurtosis())
            }
        
        # Categorical statistics
        for col in categorical_cols:
            series = df[col].dropna()
            value_counts = series.value_counts().head(10)
            stats['categorical_stats'][col] = {
                'count': len(series),
                'unique_values': int(series.nunique()),
                'top_values': {str(k): int(v) for k, v in value_counts.items()}
            }
        
        return stats
    
    def _correlation_analysis(self, df):
        """Perform correlation analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation analysis'}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:
                    corr_value = corr_matrix.loc[col1, col2]
                    if not pd.isna(corr_value) and abs(corr_value) > 0.5:
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': float(corr_value)
                        })
        
        # Sort by absolute correlation strength
        strong_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'numeric_columns': list(numeric_cols)
        }
    
    def _data_profiling(self, df):
        """Profile data quality and structure"""
        profile = {
            'overview': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'total_cells': len(df) * len(df.columns)
            },
            'missing_values': {},
            'data_types': {},
            'quality_issues': []
        }
        
        # Missing values analysis
        missing_counts = df.isnull().sum()
        for col, count in missing_counts.items():
            if count > 0:
                profile['missing_values'][col] = {
                    'count': int(count),
                    'percentage': float(count / len(df) * 100)
                }
        
        # Data types
        for col, dtype in df.dtypes.items():
            profile['data_types'][col] = str(dtype)
        
        # Quality issues
        total_missing = missing_counts.sum()
        if total_missing > 0:
            profile['quality_issues'].append(f"Found {total_missing} missing values")
        
        # Check for potential duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            profile['quality_issues'].append(f"Found {duplicate_count} potential duplicate rows")
        
        return profile
    
    def _visualization_analysis(self, df, parameters):
        """Suggest visualizations for the data"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        suggestions = []
        
        # Histogram suggestions for numeric columns
        for col in numeric_cols[:5]:
            suggestions.append({
                'type': 'histogram',
                'column': col,
                'description': f'Distribution of {col}'
            })
        
        # Bar chart suggestions for categorical columns
        for col in categorical_cols[:5]:
            unique_count = df[col].nunique()
            if unique_count <= 20:  # Only suggest for reasonable number of categories
                suggestions.append({
                    'type': 'bar_chart',
                    'column': col,
                    'description': f'Frequency of {col} categories'
                })
        
        # Scatter plot suggestions for numeric pairs
        if len(numeric_cols) >= 2:
            for i, col1 in enumerate(numeric_cols[:3]):
                for col2 in numeric_cols[i+1:4]:
                    suggestions.append({
                        'type': 'scatter_plot',
                        'x_column': col1,
                        'y_column': col2,
                        'description': f'Relationship between {col1} and {col2}'
                    })
        
        return {
            'suggestions': suggestions,
            'data_summary': {
                'numeric_columns': len(numeric_cols),
                'categorical_columns': len(categorical_cols)
            }
        }
    
    def _anomaly_detection(self, df):
        """Detect anomalies using IQR method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        anomalies = {}
        
        for col in numeric_cols:
            series = df[col].dropna()
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            if len(outliers) > 0:
                anomalies[col] = {
                    'count': len(outliers),
                    'percentage': float(len(outliers) / len(series) * 100),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'outlier_values': outliers.head(10).tolist()
                }
        
        return {
            'anomalies_by_column': anomalies,
            'total_anomalies': sum(len(v['outlier_values']) for v in anomalies.values()),
            'columns_analyzed': len(numeric_cols)
        }
    
    def _time_series_analysis(self, df, parameters):
        """Basic time series analysis"""
        # Try to identify time columns
        datetime_cols = df.select_dtypes(include=['datetime']).columns
        potential_time_cols = []
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', '日期', '时间']):
                potential_time_cols.append(col)
        
        if len(datetime_cols) == 0 and len(potential_time_cols) == 0:
            return {'error': 'No time-related columns found for time series analysis'}
        
        # Use the first available time column
        time_col = list(datetime_cols)[0] if datetime_cols else potential_time_cols[0]
        
        # Basic time series statistics
        if time_col in datetime_cols:
            time_series = df[time_col]
            return {
                'time_column': time_col,
                'date_range': {
                    'start': str(time_series.min()),
                    'end': str(time_series.max())
                },
                'total_records': len(df),
                'frequency_analysis': 'Time series analysis requires more specific implementation'
            }
        else:
            return {
                'potential_time_column': time_col,
                'suggestion': f'Column {time_col} might contain time data but needs to be converted to datetime format'
            }