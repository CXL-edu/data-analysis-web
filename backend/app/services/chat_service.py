"""
Chat service for AI conversations with database integration
"""
import pandas as pd
import numpy as np
from datetime import datetime
from flask import current_app
from app.extensions import db
from database.repositories.message_repository import MessageRepository
from app.utils.exceptions import NotFoundError, ValidationError


class ChatService:
    def __init__(self):
        self.message_repo = MessageRepository()
    
    def save_message(self, session_id, message_type, content):
        """Save a message to the database"""
        return self.message_repo.create_message(
            session_id=session_id,
            message_type=message_type,
            content=content
        )
    
    def get_message_by_id(self, message_id):
        """Get message by ID"""
        message = self.message_repo.find_by_id(message_id)
        if not message:
            raise NotFoundError('Message not found')
        return message
    
    def delete_message(self, message_id):
        """Delete a message"""
        message = self.get_message_by_id(message_id)
        return self.message_repo.delete_message(message_id)
    
    def clear_session_messages(self, session_id):
        """Clear all messages in a session"""
        return self.message_repo.delete_by_session_id(session_id)
    
    def generate_ai_response(self, session_id, message, session_files=None):
        """Generate AI response with streaming"""
        # Load data from uploaded files if available
        dataframes = []
        if session_files:
            for file_record in session_files:
                try:
                    df = self._load_dataframe(file_record)
                    if df is not None:
                        dataframes.append((file_record.filename, df))
                except Exception as e:
                    current_app.logger.warning(f"Could not load file {file_record.filename}: {e}")
        
        # Generate response based on available data
        if dataframes:
            # Use the first dataframe for analysis
            main_df = dataframes[0][1]
            response = self._process_data_question(message, main_df)
        else:
            response = self._process_general_question(message)
        
        # Simulate streaming by yielding chunks
        chunk_size = 20
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            yield chunk
    
    def _load_dataframe(self, file_record):
        """Load dataframe from uploaded file"""
        import os
        
        if not os.path.exists(file_record.file_path):
            return None
        
        file_extension = file_record.filename.rsplit('.', 1)[1].lower()
        
        try:
            if file_extension == 'csv':
                return pd.read_csv(file_record.file_path)
            elif file_extension in ['xlsx', 'xls']:
                return pd.read_excel(file_record.file_path)
            else:
                return None
        except Exception as e:
            current_app.logger.error(f"Error loading dataframe from {file_record.filename}: {e}")
            return None
    
    def _process_data_question(self, message, df):
        """Process question about data using the original chat service logic"""
        message_lower = message.lower().strip()
        
        # Route to appropriate handler based on keywords
        if self._contains_keywords(message_lower, ['概览', 'summary', 'describe', '描述', '总结']):
            return self._handle_summary_request(df)
        
        elif self._contains_keywords(message_lower, ['缺失', 'missing', 'null', '空值', 'nan']):
            return self._handle_missing_values_request(df)
        
        elif self._contains_keywords(message_lower, ['相关性', 'correlation', '关联', '相关']):
            return self._handle_correlation_request(df)
        
        elif self._contains_keywords(message_lower, ['分布', 'distribution', '统计', 'stats']):
            return self._handle_distribution_request(df)
        
        elif self._contains_keywords(message_lower, ['异常值', 'outlier', '离群值', '异常']):
            return self._handle_outliers_request(df)
        
        elif self._contains_keywords(message_lower, ['列', 'column', 'columns', '字段', 'field']):
            return self._handle_columns_request(df, message_lower)
        
        elif self._contains_keywords(message_lower, ['行', 'row', 'rows', '记录', 'record']):
            return self._handle_rows_request(df)
        
        elif self._contains_keywords(message_lower, ['类型', 'type', 'dtype', '数据类型']):
            return self._handle_dtypes_request(df)
        
        elif self._contains_keywords(message_lower, ['内存', 'memory', '大小', 'size']):
            return self._handle_memory_request(df)
        
        else:
            return self._handle_general_request(df, message)
    
    def _process_general_question(self, message):
        """Process general question without data"""
        return f"您好！我是AI数据分析助手。目前会话中没有上传的数据文件，请先上传数据文件（支持CSV、Excel格式），然后我就能帮您分析数据了。\n\n您可以上传文件后询问：\n• 数据概览\n• 缺失值分析\n• 相关性分析\n• 数据分布\n• 异常值检测\n等问题。"
    
    def _contains_keywords(self, message, keywords):
        """Check if message contains any of the keywords"""
        return any(keyword in message for keyword in keywords)
    
    def _handle_summary_request(self, df):
        """Handle data summary requests"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        response = f"📊 数据概览:\n\n"
        response += f"🔹 总行数: {len(df):,}\n"
        response += f"🔹 总列数: {len(df.columns)}\n"
        response += f"🔹 数值列: {len(numeric_cols)} 个\n"
        response += f"🔹 分类列: {len(categorical_cols)} 个\n\n"
        
        # Memory usage
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        response += f"💾 内存使用: {memory_mb:.2f} MB\n\n"
        
        # Missing values summary
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            response += f"⚠️ 缺失值: {missing_total:,} 个 ({missing_total/(len(df)*len(df.columns))*100:.1f}%)\n\n"
        else:
            response += "✅ 无缺失值\n\n"
        
        # Numeric columns statistics
        if len(numeric_cols) > 0:
            response += "📈 数值列统计 (前5列):\n"
            for col in numeric_cols[:5]:
                mean_val = df[col].mean()
                std_val = df[col].std()
                response += f"  • {col}: 平均值 {mean_val:.2f} (标准差 {std_val:.2f})\n"
            if len(numeric_cols) > 5:
                response += f"  ... 还有 {len(numeric_cols)-5} 个数值列\n"
        
        return response
    
    def _handle_missing_values_request(self, df):
        """Handle missing values analysis requests"""
        missing_info = df.isnull().sum()
        missing_cols = missing_info[missing_info > 0]
        
        if len(missing_cols) == 0:
            return "✅ 恭喜！数据中没有发现任何缺失值。"
        
        response = f"⚠️ 发现 {len(missing_cols)} 个列有缺失值:\n\n"
        
        for col, count in missing_cols.head(10).items():
            percentage = (count / len(df)) * 100
            response += f"🔸 {col}: {count:,} 个缺失值 ({percentage:.1f}%)\n"
        
        if len(missing_cols) > 10:
            response += f"\n... 还有 {len(missing_cols)-10} 个列有缺失值"
        
        total_missing = missing_info.sum()
        total_cells = len(df) * len(df.columns)
        response += f"\n\n📊 总计: {total_missing:,} 个缺失值 / {total_cells:,} 个总单元格 ({total_missing/total_cells*100:.1f}%)"
        
        return response
    
    def _handle_correlation_request(self, df):
        """Handle correlation analysis requests"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return "❌ 数据中的数值列不足以进行相关性分析。需要至少2个数值列。"
        
        corr_matrix = df[numeric_cols].corr()
        
        response = f"🔗 数值列相关性分析 ({len(numeric_cols)} 个数值列):\n\n"
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append((col1, col2, corr_value))
        
        if strong_correlations:
            response += "💪 强相关性 (|相关系数| > 0.7):\n"
            for col1, col2, corr in strong_correlations[:5]:
                emoji = "📈" if corr > 0 else "📉"
                response += f"  {emoji} {col1} ↔ {col2}: {corr:.3f}\n"
        else:
            response += "📊 未发现强相关性 (|相关系数| > 0.7)\n"
        
        response += f"\n💡 建议查看相关性热力图以获得完整的相关性矩阵。"
        
        return response
    
    def _handle_distribution_request(self, df):
        """Handle distribution analysis requests"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return "❌ 没有找到数值列用于分布分析。"
        
        response = f"📊 数据分布信息 ({len(numeric_cols)} 个数值列):\n\n"
        
        for col in numeric_cols[:5]:
            series = df[col].dropna()
            
            response += f"🔹 {col}:\n"
            response += f"  • 范围: {series.min():.2f} ~ {series.max():.2f}\n"
            response += f"  • 均值: {series.mean():.2f}, 中位数: {series.median():.2f}\n"
            response += f"  • 标准差: {series.std():.2f}\n"
            response += f"  • 偏度: {series.skew():.2f} "
            
            if abs(series.skew()) > 1:
                response += "(高度偏斜)"
            elif abs(series.skew()) > 0.5:
                response += "(中度偏斜)"
            else:
                response += "(接近正态)"
            response += "\n\n"
        
        if len(numeric_cols) > 5:
            response += f"... 还有 {len(numeric_cols)-5} 个数值列\n"
        
        response += "💡 建议生成直方图查看具体分布形状。"
        
        return response
    
    def _handle_outliers_request(self, df):
        """Handle outliers detection requests"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return "❌ 没有找到数值列用于异常值检测。"
        
        response = "🎯 异常值检测 (IQR方法):\n\n"
        
        total_outliers = 0
        for col in numeric_cols[:5]:
            series = df[col].dropna()
            
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_count = len(outliers)
            total_outliers += outlier_count
            
            response += f"🔸 {col}: {outlier_count} 个异常值 "
            response += f"({outlier_count/len(series)*100:.1f}%)\n"
            
            if outlier_count > 0:
                response += f"  范围: [{lower_bound:.2f}, {upper_bound:.2f}]\n"
        
        if len(numeric_cols) > 5:
            response += f"\n... 还有 {len(numeric_cols)-5} 个数值列需要检测\n"
        
        response += f"\n📊 总计发现 {total_outliers} 个异常值"
        response += "\n\n💡 建议使用箱线图可视化异常值分布。"
        
        return response
    
    def _handle_columns_request(self, df, message):
        """Handle column-related requests"""
        response = f"📋 列信息:\n\n"
        response += f"🔹 总列数: {len(df.columns)}\n\n"
        
        # Group columns by type
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime']).columns
        
        if len(numeric_cols) > 0:
            response += f"📊 数值列 ({len(numeric_cols)} 个):\n"
            for col in numeric_cols[:10]:
                response += f"  • {col} ({df[col].dtype})\n"
            if len(numeric_cols) > 10:
                response += f"  ... 还有 {len(numeric_cols)-10} 个\n"
            response += "\n"
        
        if len(categorical_cols) > 0:
            response += f"📝 分类列 ({len(categorical_cols)} 个):\n"
            for col in categorical_cols[:10]:
                unique_count = df[col].nunique()
                response += f"  • {col} ({unique_count} 个唯一值)\n"
            if len(categorical_cols) > 10:
                response += f"  ... 还有 {len(categorical_cols)-10} 个\n"
            response += "\n"
        
        if len(datetime_cols) > 0:
            response += f"📅 日期列 ({len(datetime_cols)} 个):\n"
            for col in datetime_cols:
                response += f"  • {col}\n"
        
        return response
    
    def _handle_rows_request(self, df):
        """Handle row-related requests"""
        response = f"📏 行信息:\n\n"
        response += f"🔹 总行数: {len(df):,}\n"
        response += f"🔹 完整行数: {df.dropna().shape[0]:,}\n"
        response += f"🔹 有缺失值的行数: {(len(df) - df.dropna().shape[0]):,}\n\n"
        
        # Memory per row
        memory_per_row = df.memory_usage(deep=True).sum() / len(df)
        response += f"💾 平均每行内存: {memory_per_row:.2f} bytes\n"
        
        return response
    
    def _handle_dtypes_request(self, df):
        """Handle data types requests"""
        response = "🏷️ 数据类型分布:\n\n"
        
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            response += f"🔹 {dtype}: {count} 列\n"
        
        response += "\n📋 各列详细类型:\n"
        for col, dtype in df.dtypes.items()[:15]:
            response += f"  • {col}: {dtype}\n"
        
        if len(df.columns) > 15:
            response += f"  ... 还有 {len(df.columns)-15} 列\n"
        
        return response
    
    def _handle_memory_request(self, df):
        """Handle memory usage requests"""
        memory_usage = df.memory_usage(deep=True)
        total_memory = memory_usage.sum()
        
        response = f"💾 内存使用情况:\n\n"
        response += f"🔹 总内存: {total_memory / (1024*1024):.2f} MB\n"
        response += f"🔹 索引内存: {memory_usage.iloc[0] / 1024:.2f} KB\n\n"
        
        # Top memory consuming columns
        column_memory = memory_usage.iloc[1:].sort_values(ascending=False)
        response += "📊 内存占用最大的列 (前5个):\n"
        for col, mem in column_memory.head(5).items():
            response += f"  • {col}: {mem / 1024:.2f} KB ({mem/total_memory*100:.1f}%)\n"
        
        return response
    
    def _handle_general_request(self, df, message):
        """Handle general or unrecognized requests"""
        response = f"🤔 我理解您想了解关于数据的信息。\n\n"
        response += f"📊 当前数据集有 {len(df)} 行，{len(df.columns)} 列。\n\n"
        response += "您可以询问我以下问题:\n\n"
        response += "📋 **数据概览**: '数据概览'、'总结'、'describe'\n"
        response += "⚠️ **缺失值**: '缺失值'、'missing values'\n"
        response += "🔗 **相关性**: '相关性分析'、'correlation'\n"
        response += "📊 **分布**: '数据分布'、'distribution'\n"
        response += "🎯 **异常值**: '异常值'、'outliers'\n"
        response += "📋 **列信息**: '列信息'、'columns'\n"
        response += "🏷️ **数据类型**: '数据类型'、'dtypes'\n"
        response += "💾 **内存使用**: '内存使用'、'memory'\n\n"
        response += "或者直接告诉我您想了解哪个具体的列或数据特征！"
        
        return response