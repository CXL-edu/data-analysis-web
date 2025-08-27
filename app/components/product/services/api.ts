// API service for communicating with authenticated Flask backend

const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

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
  message: string;
  preview_data?: DataRow[];
  columns?: string[];
  stats?: {
    rows: number;
    columns: number;
    memory_usage: number;
    dtypes: { [key: string]: string };
  };
}

export interface Session {
  id: number;
  uuid: string;
  title: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  message_count?: number;
  file_count?: number;
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

export interface StreamMessage {
  type: 'text' | 'thought' | 'image' | 'tool_call' | 'done' | 'error';
  content: string;
}

export type StreamCallback = (message: StreamMessage) => void;

class ApiService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async getUserSessions(): Promise<Session[]> {
    try {
      console.log('Fetching sessions from:', `${API_BASE_URL}/sessions/`);
      console.log('Auth headers:', this.getAuthHeaders());
      
      const response = await fetch(`${API_BASE_URL}/sessions/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        let errorMessage = 'Failed to fetch sessions';
        try {
          const error = await response.json();
          console.log('Error response:', error);
          errorMessage = error.message || error.error || errorMessage;
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          if (response.status === 401) {
            errorMessage = 'Authentication failed. Please login again.';
          } else if (response.status === 404) {
            errorMessage = 'Sessions endpoint not found.';
          } else {
            errorMessage = `Server error: ${response.status} ${response.statusText}`;
          }
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Sessions data:', data);
      return data;
    } catch (error) {
      console.error('Fetch error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async createSession(title?: string): Promise<Session> {
    console.log('Creating session with title:', title);
    console.log('API URL:', `${API_BASE_URL}/sessions/`);
    console.log('Auth headers:', this.getAuthHeaders());

    const requestData = { title: title || '新对话' };
    console.log('Request data:', requestData);

    try {
      const response = await fetch(`${API_BASE_URL}/sessions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        body: JSON.stringify(requestData),
      });

      console.log('Create session response status:', response.status);
      console.log('Create session response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Create session failed with response:', errorText);
        
        let errorMessage = 'Failed to create session';
        try {
          const error = JSON.parse(errorText);
          errorMessage = error.message || error.error || errorMessage;
        } catch (e) {
          errorMessage = `Create session failed: ${response.status} ${response.statusText}`;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Session created successfully:', result);
      return result;
    } catch (error) {
      console.error('Create session error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async uploadFile(file: File, sessionId: string): Promise<UploadResponse> {
    console.log('Starting file upload:', {
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      sessionId: sessionId
    });

    const formData = new FormData();
    formData.append('file', file);

    const uploadUrl = `${API_BASE_URL}/files/upload/${sessionId}`;
    console.log('Upload URL:', uploadUrl);
    console.log('Auth headers:', this.getAuthHeaders());

    try {
      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          ...this.getAuthHeaders(),
        },
        body: formData,
      });

      console.log('Upload response status:', response.status);
      console.log('Upload response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload failed with response:', errorText);
        
        let errorMessage = 'Upload failed';
        try {
          const error = JSON.parse(errorText);
          errorMessage = error.message || error.error || errorMessage;
        } catch (e) {
          errorMessage = `Upload failed: ${response.status} ${response.statusText}`;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      return result;
    } catch (error) {
      console.error('Upload error:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async analyzeData(sessionId: string, analysisType: string = 'summary'): Promise<AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify({
        session_id: sessionId,
        analysis_type: analysisType,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Analysis failed');
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

    const response = await fetch(`${API_BASE_URL}/analysis/chart`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Chart generation failed');
    }

    return response.json();
  }

  async chatWithData(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Chat failed');
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${API_BASE_URL}/health`, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }

    return response.json();
  }

  async streamChat(
    sessionId: string, 
    message: string, 
    onMessage: StreamCallback
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Streaming failed');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = line.slice(6); // Remove 'data: ' prefix
              if (data.trim()) {
                const message: StreamMessage = JSON.parse(data);
                onMessage(message);
                
                // Stop if we receive 'done' message
                if (message.type === 'done') {
                  return;
                }
              }
            } catch (e) {
              console.warn('Failed to parse SSE message:', line, e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export const apiService = new ApiService();