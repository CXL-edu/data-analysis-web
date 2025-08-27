'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Icon from '../product/common/Icon';
import VerificationForm from './VerificationForm';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onClose: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSwitchToLogin, onClose }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const { sendRegistrationCode, isLoading } = useAuth();

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!username || !email || !password || !confirmPassword) {
      setError('请填写所有必填字段');
      return;
    }

    if (password !== confirmPassword) {
      setError('密码和确认密码不匹配');
      return;
    }

    if (password.length < 6) {
      setError('密码长度不能少于6位');
      return;
    }

    try {
      await sendRegistrationCode(username, email, password);
      setShowVerification(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : '注册失败');
    }
  };

  const handleVerificationSuccess = () => {
    setSuccess(true);
    setCountdown(3);
    // 3秒后自动跳转到登录页面
    setTimeout(() => {
      onSwitchToLogin();
    }, 3000);
  };

  const handleBackToRegister = () => {
    setShowVerification(false);
    setError('');
  };

  // 显示验证码输入界面
  if (showVerification) {
    return (
      <VerificationForm
        email={email}
        onVerifySuccess={handleVerificationSuccess}
        onBack={handleBackToRegister}
        onClose={onClose}
      />
    );
  }

  if (success) {
    return (
      <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Icon name="check" className="text-green-600" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">注册成功！</h2>
          <p className="text-gray-600 mb-4">
            您的账户已成功创建并通过邮箱验证，现在可以登录使用了。
          </p>
          {countdown > 0 && (
            <p className="text-sm text-gray-500 mb-4">
              {countdown} 秒后将自动跳转到登录页面
            </p>
          )}
          <button
            onClick={onSwitchToLogin}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
          >
            立即登录
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">注册</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <Icon name="x" size={20} className="text-gray-500" />
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
            用户名
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入用户名"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            邮箱地址
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入您的邮箱"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            密码
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请输入密码（至少6位）"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
            确认密码
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请再次输入密码"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '注册中...' : '注册'}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          已有账号？{' '}
          <button
            onClick={onSwitchToLogin}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            立即登录
          </button>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;