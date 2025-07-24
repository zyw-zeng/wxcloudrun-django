from rest_framework import serializers
from .models import Note, Category

class CategorySerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'note_count', 'created_at']
    
    def get_note_count(self, obj):
        return Note.objects.filter(category=obj, is_deleted=False).count()

class NoteSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'category', 'category_name', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'is_deleted': {'write_only': True}
        }
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''

class NoteListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content_preview', 'category', 'category_name', 'created_at', 'updated_at']
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''
    
    def get_content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content 