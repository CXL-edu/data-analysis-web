// API service for communicating with Flask backend

const API_BASE_URL = 'http://localhost:5000/api';

export interface DataRow {
  [key: string]: string | number;
}

export interface ChartData {
  type: 'bar' | 'line' | 'pie';
  title: string;
  data: any[];
  image?: string;
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  preview_data: DataRow[];
  columns: string[];
  stats: {
    rows: number;
    columns: number;
    memory_usage: number;
    dtypes: { [key: string]: string };
  };
  message: string;
}

export interface AnalysisResponse {
  session_id: string;
  analysis_type: string;
  results: any;
  timestamp: string;
}

export interface ChartResponse {
  session_id: string;
  chart_type: string;
  chart_image: string;
  chart_data: any;
  timestamp: string;
}

export interface ChatResponse {
  session_id: string;
  user_message: string;
  ai_response: string;
  timestamp: string;
}

class ApiService {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload failed');
    }

    return response.json();
  }

  async analyzeData(sessionId: string, analysisType: string = 'summary'): Promise<AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        analysis_type: analysisType,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Analysis failed');
    }

    return response.json();
  }

  async generateChart(
    sessionId: string,
    chartType: string,
    column?: string,
    xColumn?: string,
    yColumn?: string
  ): Promise<ChartResponse> {
    const payload: any = {
      session_id: sessionId,
      chart_type: chartType,
    };

    if (column) payload.column = column;
    if (xColumn) payload.x_column = xColumn;
    if (yColumn) payload.y_column = yColumn;

    const response = await fetch(`${API_BASE_URL}/generate_chart`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Chart generation failed');
    }

    return response.json();
  }

  async chatWithData(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Chat failed');
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }

    return response.json();
  }
}

export const apiService = new ApiService();