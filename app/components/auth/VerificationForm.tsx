'use client';

import React, { useState, useEffect } from 'react';
import Icon from '../product/common/Icon';

interface VerificationFormProps {
  email: string;
  onVerifySuccess: () => void;
  onBack: () => void;
  onClose: () => void;
}

const VerificationForm: React.FC<VerificationFormProps> = ({ 
  email, 
  onVerifySuccess, 
  onBack, 
  onClose 
}) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [countdown, setCountdown] = useState(0);

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

    if (!code || code.length !== 6) {
      setError('请输入6位验证码');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/v1/auth/verify-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email,
          code: code 
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || '验证失败');
      }

      onVerifySuccess();
    } catch (error) {
      setError(error instanceof Error ? error.message : '验证失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError('');
    setCountdown(60);
    
    try {
      // 调用重新发送接口
      const response = await fetch('http://127.0.0.1:5000/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || '重新发送失败');
      }

      // 成功提示
      setError(''); // 清除错误
      // 可以考虑添加成功提示，但这里我们只是清除错误
    } catch (error) {
      setError(error instanceof Error ? error.message : '重新发送验证码失败');
      setCountdown(0);
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(value);
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">邮箱验证</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <Icon name="x" size={20} className="text-gray-500" />
        </button>
      </div>

      <div className="mb-6 text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="mail" className="text-blue-600" size={32} />
        </div>
        <p className="text-gray-600 mb-2">
          验证码已发送到
        </p>
        <p className="font-medium text-gray-900 mb-4">
          {email}
        </p>
        <p className="text-sm text-gray-500">
          请查收并输入6位数字验证码
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-300 rounded-md text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
            验证码
          </label>
          <input
            type="text"
            id="code"
            value={code}
            onChange={handleCodeChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-2xl font-mono tracking-wider"
            placeholder="000000"
            maxLength={6}
            disabled={isLoading}
            autoComplete="off"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || code.length !== 6}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? '验证中...' : '确认验证'}
        </button>
      </form>

      <div className="mt-6 flex items-center justify-between text-sm">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-gray-800 flex items-center"
        >
          <Icon name="arrow-left" size={16} className="mr-1" />
          返回注册
        </button>
        
        <div className="text-center">
          {countdown > 0 ? (
            <span className="text-gray-500">
              {countdown}秒后可重新发送
            </span>
          ) : (
            <button
              onClick={handleResendCode}
              className="text-blue-600 hover:text-blue-800"
            >
              重新发送验证码
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default VerificationForm;