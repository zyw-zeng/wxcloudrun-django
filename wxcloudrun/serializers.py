from rest_framework import serializers
from .models import Note, Category, WxUser

class CategorySerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'note_count', 'created_at']
    
    def get_note_count(self, obj):
        return Note.objects.filter(category=obj, is_deleted=False).count()

class WxUserSerializer(serializers.ModelSerializer):
    """微信用户序列化器"""
    class Meta:
        model = WxUser
        fields = ['id', 'nickname', 'avatar_url', 'gender', 'created_at', 'last_login']
        read_only_fields = ['id', 'created_at', 'last_login']

class WxLoginSerializer(serializers.Serializer):
    """微信登录序列化器"""
    code = serializers.CharField(max_length=100, required=True)
    nickname = serializers.CharField(max_length=100, required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    gender = serializers.IntegerField(required=False, default=0)

class NoteSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'category', 'category_name', 
                 'attachment', 'attachment_name', 'attachment_type', 'attachment_url',
                 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'attachment_name', 'attachment_type', 'attachment_url']
        extra_kwargs = {
            'is_deleted': {'write_only': True},
            'attachment': {'write_only': True}
        }
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''
        
    def get_attachment_url(self, obj):
        if obj.attachment and hasattr(obj.attachment, 'url'):
            return obj.attachment.url
        return None

class NoteListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content_preview', 'category', 'category_name', 
                 'has_attachment', 'attachment_type', 'created_at', 'updated_at']
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''
    
    def get_content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        
    def get_has_attachment(self, obj):
        return bool(obj.attachment) 