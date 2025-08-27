# AI Data Assistant Backend

A professional Flask-based backend service for the AI Data Analysis Assistant, providing RESTful APIs for data processing, analysis, and visualization.

## 🏗️ Project Structure

```
backend/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── api/                     # API blueprints
│   │   ├── __init__.py
│   │   └── routes.py            # API route handlers
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── file_handler.py      # File processing service
│   │   ├── data_analyzer.py     # Data analysis service
│   │   ├── chart_generator.py   # Chart generation service
│   │   └── chat_service.py      # Chat interaction service
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       └── session_manager.py   # Session management
├── uploads/                     # File upload directory
├── tests/                       # Test files
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

5. **Start the server**
   ```bash
   python run.py
   ```

The server will start at `http://localhost:5000`

## 📡 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
Currently, no authentication is required. Sessions are managed via session IDs.

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

#### 2. File Upload
```http
POST /api/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: Data file (CSV, Excel, ODS)

**Response:**
```json
{
  "session_id": "data_csv_20240101_120000_123456",
  "filename": "data.csv",
  "preview_data": [...],
  "columns": ["col1", "col2", ...],
  "stats": {
    "rows": 1000,
    "columns": 5,
    "numeric_columns": 3,
    "categorical_columns": 2,
    "missing_values": 10
  },
  "message": "Successfully processed data.csv..."
}
```

#### 3. Data Analysis
```http
POST /api/analyze
Content-Type: application/json
```

**Parameters:**
```json
{
  "session_id": "session_id",
  "analysis_type": "summary|correlation|missing_values|distribution|outliers"
}
```

**Response:**
```json
{
  "session_id": "session_id",
  "analysis_type": "summary",
  "results": {...},
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 4. Chart Generation
```http
POST /api/generate_chart
Content-Type: application/json
```

**Parameters:**
```json
{
  "session_id": "session_id",
  "chart_type": "histogram|correlation|scatter|box_plot|bar_chart|line_chart",
  "column": "column_name",
  "x_column": "x_column_name",
  "y_column": "y_column_name"
}
```

**Response:**
```json
{
  "session_id": "session_id",
  "chart_type": "histogram",
  "chart_image": "base64_encoded_image",
  "chart_data": {...},
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 5. Chat with Data
```http
POST /api/chat
Content-Type: application/json
```

**Parameters:**
```json
{
  "session_id": "session_id",
  "message": "用户问题"
}
```

**Response:**
```json
{
  "session_id": "session_id",
  "user_message": "用户问题",
  "ai_response": "AI回答",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 6. Delete Session
```http
DELETE /api/sessions/<session_id>
```

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

## 🔧 Configuration

The application supports multiple configuration environments:

- **Development** (`FLASK_CONFIG=development`)
- **Production** (`FLASK_CONFIG=production`)
- **Testing** (`FLASK_CONFIG=testing`)

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_CONFIG` | Configuration environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `true` |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | `16777216` (16MB) |
| `SESSION_TIMEOUT_HOURS` | Session timeout | `2` |
| `CHART_DPI` | Chart image DPI | `150` |
| `MAX_CORRELATION_FEATURES` | Max features for correlation | `20` |

## 🛠️ Services

### FileHandler
Handles file upload, validation, and processing for CSV, Excel, and ODS formats.

**Key Features:**
- Multi-format support (CSV, XLSX, XLS, ODS)
- Encoding detection for CSV files
- File validation and security
- Memory-efficient processing

### DataAnalyzer
Provides comprehensive data analysis capabilities.

**Analysis Types:**
- **Summary**: Basic statistics, data types, missing values
- **Correlation**: Correlation matrix and strong relationships
- **Missing Values**: Detailed missing value analysis
- **Distribution**: Statistical distribution analysis
- **Outliers**: IQR-based outlier detection

### ChartGenerator
Generates publication-quality charts using Matplotlib and Seaborn.

**Chart Types:**
- **Histogram**: Distribution visualization
- **Correlation Heatmap**: Correlation matrix visualization
- **Scatter Plot**: Relationship between variables
- **Box Plot**: Outlier and distribution visualization
- **Bar Chart**: Categorical data visualization
- **Line Chart**: Trend visualization

### ChatService
Provides intelligent responses to natural language queries about data.

**Supported Queries:**
- Data overview and summary
- Missing values analysis
- Correlation insights
- Distribution information
- Column and data type information
- Memory usage statistics

### SessionManager
Thread-safe session management with automatic cleanup.

**Features:**
- In-memory session storage
- Automatic session expiration
- Thread-safe operations
- Memory management

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-flask requests

# Run all tests
pytest

# Run specific test
pytest tests/test_api.py

# Run with coverage
pytest --cov=app
```

## 📊 Performance Considerations

### Memory Management
- Sessions are stored in memory with automatic cleanup
- Large datasets are processed in chunks where possible
- Charts are generated and immediately cleaned up

### Scalability
- Thread-safe session management
- Stateless API design
- Configurable resource limits

### Security
- File type validation
- Secure filename handling
- CORS protection
- Input sanitization

## 🚦 Monitoring and Logging

The application provides comprehensive logging:

```python
# Application logs
current_app.logger.info("Information message")
current_app.logger.error("Error message")

# Access logs
Flask's built-in request logging
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Solution: Ensure you're in the backend directory
   cd backend
   python run.py
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port 5000
   netstat -ano | findstr :5000  # Windows
   lsof -i :5000                 # macOS/Linux
   
   # Kill the process or change port in config
   ```

3. **File Upload Fails**
   - Check file size (max 16MB)
   - Verify file format (CSV, XLSX, XLS, ODS)
   - Check file encoding for CSV files

4. **Chart Generation Issues**
   - Ensure matplotlib backend is properly configured
   - Check for sufficient numeric columns
   - Verify data quality

### Debug Mode

Enable debug mode for detailed error information:

```bash
export FLASK_DEBUG=true  # Linux/macOS
set FLASK_DEBUG=true     # Windows
```

## 📈 Future Enhancements

- Database integration for persistent storage
- User authentication and authorization
- Advanced ML analysis capabilities
- Real-time data streaming support
- Horizontal scaling with Redis/Celery
- API rate limiting and caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation