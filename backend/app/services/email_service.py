"""
Email service using SMTP (credentials from environment / .env)
"""
import os
import smtplib
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.header import Header
from email import encoders
from typing import Optional, Dict, Any, Tuple

# 修改Flask导入，避免直接运行时的上下文问题
try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    current_app = None


def _load_dotenv_once():
    """确保在非 Flask 上下文中也能从 .env 读取（仅加载一次）"""
    if os.environ.get("_DOTENV_LOADED_FOR_EMAIL"):
        return
    try:
        from dotenv import load_dotenv
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(backend_dir, ".env"))
        os.environ["_DOTENV_LOADED_FOR_EMAIL"] = "1"
    except Exception:
        pass


class EmailService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        _load_dotenv_once()
        # 鉴权信息不再硬编码，由 _get_smtp_config() 从环境变量/配置读取
        self.display_name = os.environ.get("SMTP_DISPLAY_NAME", "数源智能--AI数据分析助手")
        # 统一存储验证码和注册信息（生产环境建议使用Redis）
        self.registrations = {}  # {email: {code, expires_at, attempts, user_data}}
        self.code_expiry = 5 * 60  # 5分钟过期
        self._initialized = True

    def _get_current_time(self):
        """获取当前UTC时间，避免时区问题"""
        return datetime.now(timezone.utc)

    def _get_app_config(self, key: str, default=None):
        """安全获取Flask配置"""
        if FLASK_AVAILABLE and current_app:
            try:
                return current_app.config.get(key, default)
            except RuntimeError:
                # 没有应用上下文
                return default
        return default

    def _get_smtp_config(self) -> Tuple[str, int, str, str]:
        """
        从环境变量或 Flask 配置读取 SMTP 鉴权信息。
        环境变量：SMTP_HOST, SMTP_PORT, SMTP_FROM_EMAIL, SMTP_PASSWORD；
        或使用 Flask 邮件配置：MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER。
        返回 (smtp_host, smtp_port, from_email, password)。
        """
        _load_dotenv_once()
        host = self._get_app_config("SMTP_HOST") or self._get_app_config("MAIL_SERVER") or os.environ.get("SMTP_HOST") or os.environ.get("MAIL_SERVER")
        port_str = self._get_app_config("SMTP_PORT") or self._get_app_config("MAIL_PORT") or os.environ.get("SMTP_PORT") or os.environ.get("MAIL_PORT")
        port = int(port_str) if port_str else 465
        from_email = self._get_app_config("SMTP_FROM_EMAIL") or self._get_app_config("MAIL_DEFAULT_SENDER") or self._get_app_config("MAIL_USERNAME") or os.environ.get("SMTP_FROM_EMAIL") or os.environ.get("MAIL_DEFAULT_SENDER") or os.environ.get("MAIL_USERNAME")
        password = self._get_app_config("SMTP_PASSWORD") or self._get_app_config("MAIL_PASSWORD") or os.environ.get("SMTP_PASSWORD") or os.environ.get("MAIL_PASSWORD")
        if not host or not from_email or not password:
            raise RuntimeError(
                "SMTP 鉴权未配置。请在 .env 中设置 SMTP_HOST / SMTP_FROM_EMAIL / SMTP_PASSWORD，"
                "或 MAIL_SERVER / MAIL_USERNAME / MAIL_PASSWORD。参见 backend/.env.example"
            )
        return (host, port, from_email, password)

    def store_registration_code(self, email: str, user_data: Dict[str, Any]) -> str:
        """生成验证码并存储注册信息"""
        code = str(secrets.randbelow(1000000)).zfill(6)
        current_time = self._get_current_time()
        expires_at = current_time + timedelta(seconds=self.code_expiry)

        self.registrations[email] = {
            'code': code,
            'expires_at': expires_at,
            'attempts': 0,
            'user_data': user_data,
            'created_at': current_time
        }

        # 清理过期的注册记录
        self._cleanup_expired_registrations()
        return code

    def verify_registration_code(self, email: str, input_code: str):
        """验证注册验证码并返回用户数据"""
        if email not in self.registrations:
            return False, "注册信息不存在或已过期", None

        registration_data = self.registrations[email]
        current_time = self._get_current_time()

        # 检查是否过期
        if current_time > registration_data['expires_at']:
            del self.registrations[email]
            return False, "验证码已过期", None

        # 检查尝试次数（防止暴力破解）
        if registration_data['attempts'] >= 5:
            del self.registrations[email]
            return False, "验证尝试次数过多，请重新获取验证码", None

        # 验证码错误
        if registration_data['code'] != input_code:
            self.registrations[email]['attempts'] += 1
            return False, "验证码错误", None

        # 验证成功，返回用户数据并删除记录
        user_data = registration_data['user_data']
        del self.registrations[email]
        return True, "验证成功", user_data

    def _cleanup_expired_registrations(self):
        """清理过期的注册记录"""
        current_time = self._get_current_time()
        expired_emails = [
            email for email, data in self.registrations.items()
            if current_time > data['expires_at']
        ]
        for email in expired_emails:
            del self.registrations[email]

    def has_pending_registration(self, email: str) -> bool:
        """检查是否有待验证的注册"""
        if email not in self.registrations:
            return False

        current_time = self._get_current_time()
        expires_at = self.registrations[email]['expires_at']
        
        if current_time > expires_at:
            del self.registrations[email]
            return False
        return True

    def send_registration_email(self, to_email: str, username: str, user_data: Dict[str, Any]):
        """发送注册验证码邮件"""
        try:
            smtp_host, smtp_port, from_email, password = self._get_smtp_config()
            # 生成并存储验证码和用户数据
            code = self.store_registration_code(to_email, user_data)

            subject = "【数源智能】邮箱验证码"
            content = f"""
尊敬的用户{username}：

您正在注册数源智能AI数据分析助手，您的验证码是：

{code}

验证码有效期为5分钟，请及时输入完成验证。
如非本人操作，请忽略此邮件。

数源智能团队
            """.strip()

            # 开发模式下打印验证码
            debug_mode = self._get_app_config('DEBUG', False)
            if debug_mode:
                print(f"📧 验证码邮件 [{to_email}]: {code}")

            # 创建邮件
            msg = MIMEText(content, 'plain', 'utf-8')
            if msg.get('Content-Transfer-Encoding'):
                del msg['Content-Transfer-Encoding']
            msg.set_payload(content.encode('utf-8'))
            encoders.encode_base64(msg)
            
            msg['From'] = f"{Header(self.display_name, 'utf-8').encode()} <{from_email}>"
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')

            # 发送邮件
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(from_email, password)
                server.sendmail(from_email, [to_email], msg.as_string())

            return True, code

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP认证失败"
        except smtplib.SMTPRecipientsRefused:
            return False, "收件人被拒绝，可能邮箱不存在"
        except Exception as e:
            return False, f"发送邮件失败: {str(e)}"

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        try:
            smtp_host, smtp_port, from_email, password = self._get_smtp_config()
            subject = "欢迎使用数源智能AI数据分析助手！"

            # 安全获取前端URL
            frontend_url = self._get_app_config('FRONTEND_URL', 'http://127.0.0.1:3000')

            content = f"""
亲爱的{username}：

欢迎注册数源智能AI数据分析助手！

您现在可以：
• 上传数据文件进行智能分析
• 与AI助手对话获得数据洞察
• 生成各种可视化图表
• 导出分析结果

立即开始您的数据分析之旅：
{frontend_url}

如有任何问题，请随时联系我们的客服团队。

数源智能团队
            """.strip()

            msg = MIMEText(content, 'plain', 'utf-8')
            if msg.get('Content-Transfer-Encoding'):
                del msg['Content-Transfer-Encoding']
            msg.set_payload(content.encode('utf-8'))
            encoders.encode_base64(msg)
            
            msg['From'] = f"{Header(self.display_name, 'utf-8').encode()} <{from_email}>"
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')

            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(from_email, password)
                server.sendmail(from_email, [to_email], msg.as_string())

            return True

        except Exception as e:
            return False

    def resend_registration_code(self, email: str):
        """重新发送注册验证码"""
        if email not in self.registrations:
            return False, "没有找到待验证的注册信息，请重新注册"
        
        user_data = self.registrations[email]
        username = user_data['user_data']['username']
        
        # 重新发送验证码
        success, code_or_error = self.send_registration_email(email, username, user_data['user_data'])
        if not success:
            return False, f"重新发送验证码失败: {code_or_error}"
        
        return True, None


# 全局邮件服务实例
email_service = EmailService()
