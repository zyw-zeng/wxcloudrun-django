import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters, Note, Category
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q


logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})

# 笔记相关API
@require_http_methods(["GET"])
def note_list(request):
    """获取笔记列表"""
    try:
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        category_id = request.GET.get('category_id')
        keyword = request.GET.get('keyword', '')
        
        # 构建查询条件
        query = Q(is_deleted=False)
        if category_id:
            query &= Q(category_id=category_id)
        if keyword:
            query &= (Q(title__icontains=keyword) | Q(content__icontains=keyword))
        
        # 查询数据
        notes = Note.objects.filter(query).order_by('-updated_at')
        
        # 分页
        paginator = Paginator(notes, page_size)
        page_obj = paginator.get_page(page)
        
        # 格式化输出数据
        note_list = []
        for note in page_obj:
            category_name = note.category.name if note.category else ''
            note_list.append({
                'id': note.id,
                'title': note.title,
                'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,  # 内容摘要
                'category_id': note.category_id,
                'category_name': category_name,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'code': 0,
            'data': {
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'list': note_list
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"获取笔记列表出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'获取笔记列表失败: {str(e)}'}, 
                           json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def note_create(request):
    """创建笔记"""
    try:
        body = json.loads(request.body)
        title = body.get('title', '').strip()
        content = body.get('content', '')
        category_id = body.get('category_id')
        
        # 参数校验
        if not title:
            return JsonResponse({'code': -1, 'errorMsg': '标题不能为空'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 创建笔记
        note = Note(
            title=title,
            content=content,
        )
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                note.category = category
            except Category.DoesNotExist:
                pass
                
        note.save()
        
        return JsonResponse({
            'code': 0, 
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'category_id': note.category_id,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"创建笔记出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'创建笔记失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def note_update(request, note_id):
    """更新笔记"""
    try:
        # 查找笔记
        try:
            note = Note.objects.get(id=note_id, is_deleted=False)
        except Note.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '笔记不存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 获取更新数据
        body = json.loads(request.body)
        title = body.get('title')
        content = body.get('content')
        category_id = body.get('category_id')
        
        # 更新数据
        if title is not None:
            title = title.strip()
            if not title:
                return JsonResponse({'code': -1, 'errorMsg': '标题不能为空'}, 
                                  json_dumps_params={'ensure_ascii': False})
            note.title = title
            
        if content is not None:
            note.content = content
            
        if category_id is not None:
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    note.category = category
                except Category.DoesNotExist:
                    return JsonResponse({'code': -1, 'errorMsg': '分类不存在'}, 
                                      json_dumps_params={'ensure_ascii': False})
            else:
                note.category = None
                
        note.save()
        
        category_name = note.category.name if note.category else ''
        
        return JsonResponse({
            'code': 0, 
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'category_id': note.category_id,
                'category_name': category_name,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"更新笔记出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'更新笔记失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def note_delete(request, note_id):
    """删除笔记（软删除）"""
    try:
        # 查找笔记
        try:
            note = Note.objects.get(id=note_id, is_deleted=False)
        except Note.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '笔记不存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 软删除
        note.is_deleted = True
        note.save()
        
        return JsonResponse({'code': 0, 'data': {'id': note_id}}, 
                          json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"删除笔记出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'删除笔记失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["GET"])
def note_detail(request, note_id):
    """获取笔记详情"""
    try:
        # 查找笔记
        try:
            note = Note.objects.get(id=note_id, is_deleted=False)
        except Note.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '笔记不存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        category_name = note.category.name if note.category else ''
        
        # 返回详情
        return JsonResponse({
            'code': 0, 
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'category_id': note.category_id,
                'category_name': category_name,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"获取笔记详情出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'获取笔记详情失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

# 分类相关API
@require_http_methods(["GET"])
def category_list(request):
    """获取分类列表"""
    try:
        categories = Category.objects.all().order_by('id')
        
        category_list = []
        for category in categories:
            # 获取该分类下的笔记数量
            note_count = Note.objects.filter(category=category, is_deleted=False).count()
            
            category_list.append({
                'id': category.id,
                'name': category.name,
                'note_count': note_count,
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'code': 0,
            'data': category_list
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"获取分类列表出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'获取分类列表失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def category_create(request):
    """创建分类"""
    try:
        body = json.loads(request.body)
        name = body.get('name', '').strip()
        
        # 参数校验
        if not name:
            return JsonResponse({'code': -1, 'errorMsg': '分类名称不能为空'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 检查是否存在同名分类
        if Category.objects.filter(name=name).exists():
            return JsonResponse({'code': -1, 'errorMsg': '分类名称已存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 创建分类
        category = Category(name=name)
        category.save()
        
        return JsonResponse({
            'code': 0, 
            'data': {
                'id': category.id,
                'name': category.name,
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"创建分类出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'创建分类失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def category_update(request, category_id):
    """更新分类"""
    try:
        # 查找分类
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '分类不存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 获取更新数据
        body = json.loads(request.body)
        name = body.get('name', '').strip()
        
        # 参数校验
        if not name:
            return JsonResponse({'code': -1, 'errorMsg': '分类名称不能为空'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 检查是否存在同名分类(排除自身)
        if Category.objects.filter(name=name).exclude(id=category_id).exists():
            return JsonResponse({'code': -1, 'errorMsg': '分类名称已存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 更新分类
        category.name = name
        category.save()
        
        return JsonResponse({
            'code': 0, 
            'data': {
                'id': category.id,
                'name': category.name,
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"更新分类出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'更新分类失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})

@require_http_methods(["POST"])
def category_delete(request, category_id):
    """删除分类"""
    try:
        # 查找分类
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '分类不存在'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 检查该分类下是否有笔记
        note_count = Note.objects.filter(category=category, is_deleted=False).count()
        if note_count > 0:
            return JsonResponse({'code': -1, 'errorMsg': f'该分类下有{note_count}条笔记，无法删除'}, 
                              json_dumps_params={'ensure_ascii': False})
        
        # 删除分类
        category.delete()
        
        return JsonResponse({'code': 0, 'data': {'id': category_id}}, 
                          json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"删除分类出错: {str(e)}")
        return JsonResponse({'code': -1, 'errorMsg': f'删除分类失败: {str(e)}'}, 
                          json_dumps_params={'ensure_ascii': False})
