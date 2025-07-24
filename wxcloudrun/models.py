from datetime import datetime

from django.db import models
from django.utils import timezone


# Create your models here.
class Counters(models.Model):
    id = models.AutoField
    count = models.IntegerField(default=0)  # IntegerField不需要max_length参数
    createdAt = models.DateTimeField(default=timezone.now)  # 使用timezone.now
    updatedAt = models.DateTimeField(default=timezone.now)  # 使用timezone.now

    def __str__(self):
        return str(self.count)  # 修正为返回count的字符串形式

    class Meta:
        db_table = 'Counters'  # 数据库表名

class Category(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        db_table = 'category'
        verbose_name = '分类'
        verbose_name_plural = '分类'

class Note(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return self.title
        
    class Meta:
        db_table = 'note'
        verbose_name = '笔记'
        verbose_name_plural = '笔记'
        ordering = ['-updated_at']
