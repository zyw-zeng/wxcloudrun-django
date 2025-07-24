from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import WxUser
from .serializers import WxUserSerializer, WxLoginSerializer
from .auth import get_wx_session_info, generate_token

import logging
from django.utils import timezone

logger = logging.getLogger('log')

class WxLoginView(APIView):
    """
    微信小程序登录接口
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = WxLoginSerializer(data=request.data)
        if not serializer.validated_data:
            return Response({'code': -1, 'message': '参数错误'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 获取序列化后的数据
        code = serializer.validated_data.get('code')
        nickname = serializer.validated_data.get('nickname', '')
        avatar_url = serializer.validated_data.get('avatar_url', '')
        gender = serializer.validated_data.get('gender', 0)
        
        # 调用微信接口获取openid和session_key
        wx_session = get_wx_session_info(code)
        if not wx_session:
            return Response({'code': -1, 'message': '微信登录失败'}, status=status.HTTP_400_BAD_REQUEST)
            
        openid = wx_session['openid']
        session_key = wx_session['session_key']
        
        # 查找或创建用户
        try:
            user, created = WxUser.objects.get_or_create(openid=openid)
            
            # 更新用户信息
            if nickname:
                user.nickname = nickname
            if avatar_url:
                user.avatar_url = avatar_url
            if gender is not None:
                user.gender = gender
                
            user.session_key = session_key
            user.last_login = timezone.now()
            user.save()
            
            # 生成登录令牌
            token = generate_token(user)
            
            # 返回用户信息和令牌
            return Response({
                'code': 0,
                'data': {
                    'token': token,
                    'user': WxUserSerializer(user).data,
                    'is_new_user': created
                }
            })
        except Exception as e:
            logger.error(f"用户登录异常: {e}")
            return Response({'code': -1, 'message': '服务器错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    """
    用户个人资料接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前登录用户信息"""
        serializer = WxUserSerializer(request.user)
        return Response({
            'code': 0,
            'data': serializer.data
        })
        
    def put(self, request):
        """更新用户资料"""
        serializer = WxUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 0,
                'data': serializer.data
            })
        return Response({
            'code': -1,
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST) 