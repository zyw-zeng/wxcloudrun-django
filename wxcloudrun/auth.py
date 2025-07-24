import jwt
import requests
import datetime
import logging
import json
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from .models import WxUser

logger = logging.getLogger('log')

# 微信小程序登录URL
WX_LOGIN_URL = 'https://api.weixin.qq.com/sns/jscode2session'

def get_wx_session_info(code):
    """
    使用code调用微信接口获取openid和session_key
    """
    try:
        # 读取微信小程序配置
        appid = settings.WX_APP_ID
        appsecret = settings.WX_APP_SECRET
        
        # 构建请求参数
        params = {
            'appid': appid,
            'secret': appsecret,
            'js_code': code,
            'grant_type': 'authorization_code',
        }
        
        # 发送请求到微信接口
        response = requests.get(WX_LOGIN_URL, params=params)
        data = response.json()
        
        # 检查返回结果
        if 'errcode' in data:
            logger.error(f"获取微信session失败: {data}")
            return None
            
        return {
            'openid': data.get('openid'),
            'session_key': data.get('session_key'),
            'unionid': data.get('unionid', '')  # 如果有unionid则返回
        }
    except Exception as e:
        logger.error(f"微信登录异常: {e}")
        return None

def generate_token(wxuser):
    """
    生成JWT Token
    """
    payload = {
        'openid': wxuser.openid,
        'user_id': wxuser.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 7天过期
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

class JWTAuthentication(BaseAuthentication):
    """
    JWT认证
    """
    def authenticate(self, request):
        auth_header = get_authorization_header(request).decode('utf-8')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        try:
            # 获取token
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # 验证token
            user_id = payload.get('user_id')
            user = WxUser.objects.get(id=user_id, is_active=True)
            
            # 更新最后登录时间
            if user.last_login is None or (datetime.datetime.now() - user.last_login.replace(tzinfo=None)).days >= 1:
                user.last_login = datetime.datetime.now()
                user.save(update_fields=['last_login'])
                
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token已过期')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('无效的Token')
        except WxUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('用户不存在或已禁用')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'认证失败: {str(e)}')
            
    def authenticate_header(self, request):
        return 'Bearer' 