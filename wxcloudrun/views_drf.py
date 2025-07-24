from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Note, Category
from .serializers import NoteSerializer, NoteListSerializer, CategorySerializer
import logging

logger = logging.getLogger('log')

class NoteViewSet(viewsets.ModelViewSet):
    """
    笔记的API视图集，提供增删改查功能
    """
    permission_classes = [IsAuthenticated]  # 需要用户登录
    queryset = Note.objects.filter(is_deleted=False)
    serializer_class = NoteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        # 列表使用简化序列化器，详情使用完整序列化器
        if self.action == 'list':
            return NoteListSerializer
        return NoteSerializer
    
    def get_queryset(self):
        # 基本查询：未删除的笔记，且属于当前用户
        queryset = Note.objects.filter(is_deleted=False, user=self.request.user)
        
        # 分类筛选
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 关键词搜索
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        # 创建时关联当前用户
        serializer.save(user=self.request.user)
        logger.info(f"用户{self.request.user.id}创建笔记: {serializer.data['title']}")
        
    def perform_update(self, serializer):
        # 更新笔记
        serializer.save()
        logger.info(f"用户{self.request.user.id}更新笔记: ID={serializer.instance.id}")
    
    @action(methods=['post'], detail=True)
    def soft_delete(self, request, pk=None):
        """软删除笔记，标记is_deleted为True"""
        note = self.get_object()
        note.is_deleted = True
        note.save()
        logger.info(f"用户{request.user.id}软删除笔记: ID={note.id}")
        return Response({'id': note.id}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    分类的API视图集，提供增删改查功能
    """
    permission_classes = [IsAuthenticated]  # 需要用户登录
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def perform_create(self, serializer):
        serializer.save()
        logger.info(f"用户{self.request.user.id}创建分类: {serializer.data['name']}")
    
    def perform_update(self, serializer):
        serializer.save()
        logger.info(f"用户{self.request.user.id}更新分类: ID={serializer.instance.id}")
    
    def get_queryset(self):
        # 获取与当前用户笔记相关的分类
        user_notes = Note.objects.filter(user=self.request.user, is_deleted=False)
        category_ids = user_notes.values_list('category_id', flat=True).distinct()
        return Category.objects.filter(id__in=category_ids)
    
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        
        # 检查该分类下是否有笔记
        note_count = Note.objects.filter(category=category, user=request.user, is_deleted=False).count()
        if note_count > 0:
            return Response(
                {'error': f'该分类下有{note_count}条笔记，无法删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 执行删除
        logger.info(f"用户{request.user.id}删除分类: ID={category.id}")
        return super().destroy(request, *args, **kwargs) 