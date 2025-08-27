# Frontend Integration Guide - AI Data Assistant

## 📋 概述

本指南说明如何将现有的前端应用与新的认证和会话管理系统集成，包括用户认证、会话管理、文件上传和实时聊天功能。

## 🔄 主要变更

### 1. 认证系统变更

**之前**: 无认证，直接访问
**现在**: 基于JWT的用户认证系统

### 2. 会话管理变更

**之前**: 临时会话，无持久化
**现在**: 持久化会话，支持历史记录

### 3. API端点变更

**之前**: `/api/chat`, `/api/upload`
**现在**: `/api/v1/auth/*`, `/api/v1/sessions/*`, `/api/v1/files/*`, `/api/v1/chat/*`

## 🛠️ 前端实现需求

### 1. 认证功能

#### 登录页面
```tsx
// components/auth/LoginForm.tsx
import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

export const LoginForm = () => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const { login, loading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(credentials);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email">邮箱</label>
        <input
          type="email"
          id="email"
          value={credentials.email}
          onChange={(e) => setCredentials(prev => ({
            ...prev,
            email: e.target.value
          }))}
          required
        />
      </div>
      
      <div>
        <label htmlFor="password">密码</label>
        <input
          type="password"
          id="password"
          value={credentials.password}
          onChange={(e) => setCredentials(prev => ({
            ...prev,
            password: e.target.value
          }))}
          required
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? '登录中...' : '登录'}
      </button>

      {error && <div className="error">{error}</div>}
    </form>
  );
};
```

#### 注册页面
```tsx
// components/auth/RegisterForm.tsx
export const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const { register, loading, error } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('密码不匹配');
      return;
    }
    await register(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* 表单字段 */}
    </form>
  );
};
```

### 2. 认证Hook

```tsx
// hooks/useAuth.ts
import { useState, useContext, createContext, useEffect } from 'react';
import { authApi } from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  is_email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      // 验证token并获取用户信息
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await authApi.getProfile(token);
      setUser(response.user);
    } catch (err) {
      logout();
    }
  };

  const login = async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authApi.login(credentials);
      setToken(response.access_token);
      setUser(response.user);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    } catch (err: any) {
      setError(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.register(userData);
      // 注册成功后可以自动登录或跳转到登录页面
    } catch (err: any) {
      setError(err.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      register,
      logout,
      loading,
      error
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### 3. API服务更新

```tsx
// services/api.ts
const API_BASE_URL = 'http://localhost:5000/api/v1';

class ApiClient {
  private getHeaders(token?: string | null) {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    
    return headers;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async requestWithAuth(endpoint: string, token: string, options: RequestInit = {}) {
    return this.request(endpoint, {
      ...options,
      headers: {
        ...this.getHeaders(token),
        ...options.headers,
      },
    });
  }
}

const apiClient = new ApiClient();

// 认证API
export const authApi = {
  login: (credentials: LoginCredentials) => 
    apiClient.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  register: (userData: RegisterData) =>
    apiClient.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  getProfile: (token: string) =>
    apiClient.requestWithAuth('/auth/profile', token),

  refreshToken: (refreshToken: string) =>
    apiClient.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
};

// 会话API
export const sessionApi = {
  getSessions: (token: string) =>
    apiClient.requestWithAuth('/sessions', token),

  createSession: (token: string, title?: string) =>
    apiClient.requestWithAuth('/sessions', token, {
      method: 'POST',
      body: JSON.stringify({ title }),
    }),

  getSession: (token: string, sessionUuid: string) =>
    apiClient.requestWithAuth(`/sessions/${sessionUuid}`, token),

  updateSession: (token: string, sessionUuid: string, data: any) =>
    apiClient.requestWithAuth(`/sessions/${sessionUuid}`, token, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteSession: (token: string, sessionUuid: string) =>
    apiClient.requestWithAuth(`/sessions/${sessionUuid}`, token, {
      method: 'DELETE',
    }),
};

// 文件API
export const fileApi = {
  uploadFile: (token: string, sessionUuid: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return fetch(`${API_BASE_URL}/files/upload/${sessionUuid}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }).then(res => res.json());
  },

  getFilePreview: (token: string, fileId: number) =>
    apiClient.requestWithAuth(`/files/${fileId}/preview`, token),

  downloadFile: (token: string, fileId: number) => {
    return fetch(`${API_BASE_URL}/files/${fileId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};
```

### 4. 会话管理组件

```tsx
// components/sessions/SessionList.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { sessionApi } from '../services/api';

interface Session {
  uuid: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  file_count: number;
}

export const SessionList = () => {
  const { token } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (token) {
      loadSessions();
    }
  }, [token]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const response = await sessionApi.getSessions(token!);
      setSessions(response.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const response = await sessionApi.createSession(token!);
      setSessions(prev => [response.session, ...prev]);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div className="session-list">
      <div className="session-header">
        <h2>我的会话</h2>
        <button onClick={createNewSession}>新建会话</button>
      </div>
      
      <div className="session-items">
        {sessions.map((session) => (
          <div key={session.uuid} className="session-item">
            <h3>{session.title}</h3>
            <p>消息: {session.message_count} | 文件: {session.file_count}</p>
            <p>更新时间: {new Date(session.updated_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 5. 聊天组件更新

```tsx
// components/chat/ChatArea.tsx - 更新后的版本
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../hooks/useAuth';

interface Message {
  id: number;
  message_type: 'user' | 'ai';
  content: string;
  timestamp: string;
}

interface ChatAreaProps {
  sessionUuid: string;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ sessionUuid }) => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadMessages();
  }, [sessionUuid]);

  const loadMessages = async () => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/v1/chat/${sessionUuid}/messages`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setMessages(data.messages);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    const userMessage = input;
    setInput('');

    try {
      // 使用Server-Sent Events进行流式聊天
      const eventSource = new EventSource(
        `http://localhost:5000/api/v1/chat/${sessionUuid}/stream`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      // 发送消息数据
      await fetch(`http://localhost:5000/api/v1/chat/${sessionUuid}/stream`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      let aiResponse = '';

      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          eventSource.close();
          setIsLoading(false);
          return;
        }

        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'user_message':
              setMessages(prev => [...prev, data.message]);
              break;
            case 'ai_chunk':
              aiResponse += data.chunk;
              // 实时更新AI响应
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.message_type === 'ai') {
                  lastMessage.content = aiResponse;
                } else {
                  newMessages.push({
                    id: Date.now(),
                    message_type: 'ai',
                    content: aiResponse,
                    timestamp: new Date().toISOString(),
                  });
                }
                return newMessages;
              });
              break;
            case 'ai_complete':
              setMessages(prev => [...prev.slice(0, -1), data.message]);
              break;
            case 'error':
              console.error('Chat error:', data.error);
              setIsLoading(false);
              break;
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsLoading(false);
        console.error('SSE connection error');
      };

    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.message_type}`}>
            <div className="message-content">{message.content}</div>
            <div className="message-time">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="输入消息..."
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading}>
          {isLoading ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
};
```

### 6. 文件上传组件更新

```tsx
// components/upload/FileUpload.tsx - 更新后的版本
interface FileUploadProps {
  sessionUuid: string;
  onFileUploaded: (file: any) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ 
  sessionUuid, 
  onFileUploaded 
}) => {
  const { token } = useAuth();
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const response = await fileApi.uploadFile(token!, sessionUuid, file);
      onFileUploaded(response.file);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        onChange={handleFileUpload}
        disabled={uploading}
        accept=".csv,.xlsx,.xls"
      />
      {uploading && <div>上传中...</div>}
    </div>
  );
};
```

### 7. 路由保护

```tsx
// components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, token } = useAuth();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
```

### 8. 主应用更新

```tsx
// App.tsx - 更新后的版本
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route path="/register" element={<RegisterForm />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/sessions/:sessionUuid" element={
              <ProtectedRoute>
                <ChatInterface />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## 🔄 迁移步骤

### 第一阶段：认证系统
1. 实现认证Provider和Hook
2. 创建登录/注册页面
3. 添加路由保护
4. 更新API调用以包含认证头

### 第二阶段：会话管理
1. 创建会话列表组件
2. 更新聊天组件以使用会话UUID
3. 实现会话持久化

### 第三阶段：文件管理
1. 更新文件上传组件
2. 实现文件预览功能
3. 添加文件管理界面

### 第四阶段：优化和测试
1. 错误处理改进
2. 加载状态优化
3. 用户体验提升
4. 全面测试

## 📝 注意事项

1. **Token刷新**: 实现自动token刷新机制
2. **错误处理**: 处理网络错误和认证失败
3. **加载状态**: 提供适当的加载指示器
4. **数据同步**: 确保前后端数据一致性
5. **安全性**: 避免在客户端存储敏感信息

## 🚀 部署考虑

1. **环境变量**: 配置生产环境API端点
2. **HTTPS**: 确保生产环境使用HTTPS
3. **CORS**: 配置正确的CORS设置
4. **缓存**: 实现适当的缓存策略

通过以上指南，可以将现有前端应用平滑迁移到新的认证和会话管理系统。