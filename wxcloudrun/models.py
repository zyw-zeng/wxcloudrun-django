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

class WxUser(models.Model):
    """微信用户模型"""
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信openid')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='昵称')
    avatar_url = models.URLField(blank=True, null=True, verbose_name='头像URL')
    gender = models.SmallIntegerField(choices=((0, '未知'), (1, '男'), (2, '女')), default=0, verbose_name='性别')
    session_key = models.CharField(max_length=100, blank=True, null=True, verbose_name='会话密钥')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.nickname or self.openid
    
    class Meta:
        db_table = 'wx_user'
        verbose_name = '微信用户'
        verbose_name_plural = '微信用户'

class Category(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        db_table = 'category'
        verbose_name = '分类'
        verbose_name_plural = '分类'

def note_attachment_path(instance, filename):
    # 文件将上传到 media/notes/附件ID_文件名
    return f'notes/{instance.id}_{filename}'

class Note(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    user = models.ForeignKey(WxUser, on_delete=models.CASCADE, null=True, related_name='notes', verbose_name='用户')
    attachment = models.FileField(upload_to=note_attachment_path, null=True, blank=True, verbose_name='附件')
    attachment_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='附件名称')
    attachment_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='附件类型')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # 如果附件存在且附件名为空，则设置附件名
        if self.attachment and not self.attachment_name:
            self.attachment_name = self.attachment.name.split('/')[-1]
            # 设置附件类型
            file_extension = self.attachment_name.split('.')[-1].lower() if '.' in self.attachment_name else ''
            if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                self.attachment_type = 'image'
            elif file_extension in ['mp4', 'avi', 'mov', 'wmv']:
                self.attachment_type = 'video'
            elif file_extension in ['mp3', 'wav', 'ogg']:
                self.attachment_type = 'audio'
            else:
                self.attachment_type = 'file'
        
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'note'
        verbose_name = '笔记'
        verbose_name_plural = '笔记'
        ordering = ['-updated_at']
