"""
In-memory cache for email verification codes
"""
import time
from typing import Optional, Dict, Tuple
from threading import Lock


class VerificationCache:
    def __init__(self):
        # 存储格式：{email: (verification_code, expire_timestamp, user_data)}
        self._cache: Dict[str, Tuple[str, float, dict]] = {}
        self._lock = Lock()
        self.expire_time = 300  # 5分钟过期
    
    def set_verification_code(self, email: str, code: str, user_data: dict) -> None:
        """存储验证码和用户数据"""
        with self._lock:
            expire_at = time.time() + self.expire_time
            self._cache[email] = (code, expire_at, user_data)
            print(f"验证码已缓存: {email} -> {code} (5分钟后过期)")
    
    def get_verification_data(self, email: str) -> Optional[Tuple[str, dict]]:
        """获取验证码和用户数据"""
        with self._lock:
            if email not in self._cache:
                return None
            
            code, expire_at, user_data = self._cache[email]
            
            # 检查是否过期
            if time.time() > expire_at:
                del self._cache[email]
                print(f"验证码已过期并清除: {email}")
                return None
            
            return code, user_data
    
    def verify_and_remove(self, email: str, input_code: str) -> Optional[dict]:
        """验证验证码，成功后移除缓存，返回用户数据"""
        with self._lock:
            if email not in self._cache:
                print(f"验证失败: 邮箱 {email} 无验证码")
                return None
            
            code, expire_at, user_data = self._cache[email]
            
            # 检查是否过期
            if time.time() > expire_at:
                del self._cache[email]
                print(f"验证失败: 验证码已过期 {email}")
                return None
            
            # 验证验证码
            if code != input_code:
                print(f"验证失败: 验证码错误 {email} (输入: {input_code}, 正确: {code})")
                return None
            
            # 验证成功，移除缓存
            del self._cache[email]
            print(f"验证成功: {email}")
            return user_data
    
    def clear_expired(self) -> None:
        """清理过期的验证码"""
        with self._lock:
            current_time = time.time()
            expired_emails = []
            
            for email, (code, expire_at, user_data) in self._cache.items():
                if current_time > expire_at:
                    expired_emails.append(email)
            
            for email in expired_emails:
                del self._cache[email]
            
            if expired_emails:
                print(f"清理了 {len(expired_emails)} 个过期验证码")
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def has_verification_code(self, email: str) -> bool:
        """检查是否存在未过期的验证码"""
        with self._lock:
            if email not in self._cache:
                return False
            
            _, expire_at, _ = self._cache[email]
            if time.time() > expire_at:
                del self._cache[email]
                return False
            
            return True


# 全局验证码缓存实例
verification_cache = VerificationCache()