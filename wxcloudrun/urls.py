"""wxcloudrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from wxcloudrun import views
from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_drf import NoteViewSet, CategoryViewSet
from .views_auth import WxLoginView, UserProfileView
from django.conf import settings
from django.conf.urls.static import static

# 创建DRF路由器
router = DefaultRouter()
# 修改路由前缀，避免与通配符冲突
router.register(r'notes', NoteViewSet)
router.register(r'categories', CategoryViewSet)

# 将urlpatterns修改为列表而不是元组
urlpatterns = [
    # 计数器接口（保留原始接口）
    url(r'^api/count(/)?$', views.counter),
    
    # 微信认证接口
    path('api/wx/login', WxLoginView.as_view(), name='wx_login'),
    path('api/user/profile', UserProfileView.as_view(), name='user_profile'),
    
    # DRF API接口 - 将DRF API路由放在前面并加上api前缀
    path('api/', include(router.urls)),
    
    # DRF认证支持
    path('api-auth/', include('rest_framework.urls')),
    
    # 旧的API接口（可以保留一段时间用于兼容）
    path('api/note/list', views.note_list),
    path('api/note/create', views.note_create),
    path('api/note/update/<int:note_id>', views.note_update),
    path('api/note/delete/<int:note_id>', views.note_delete),
    path('api/note/detail/<int:note_id>', views.note_detail),
    
    path('api/category/list', views.category_list),
    path('api/category/create', views.category_create),
    path('api/category/update/<int:category_id>', views.category_update),
    path('api/category/delete/<int:category_id>', views.category_delete),
    
    # 获取主页 - 将通配符放在最后
    url(r'^(/)?$', views.index),
]

# 仅在DEBUG模式下添加媒体文件访问URL
if settings.DEBUG and not settings.USE_COS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
