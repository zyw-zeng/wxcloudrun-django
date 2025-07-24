# 笔记应用 DRF API 文档

## 概述
本文档描述了使用Django REST Framework构建的笔记应用API接口。DRF提供了更现代化、功能更丰富的API开发体验。

## 基本信息
- **基础URL**: `http://127.0.0.1:8000`
- **响应格式**: 所有API返回JSON格式数据
- **认证**: 目前不需要认证即可访问API
- **浏览器API浏览**: 在浏览器中直接访问API URL可以获得交互式界面

## API入口点

### API根目录
- **URL**: `/api/`
- **方法**: `GET`
- **描述**: 提供API的所有端点列表
- **示例响应**:
  ```json
  {
    "notes": "http://127.0.0.1:8000/api/notes/",
    "categories": "http://127.0.0.1:8000/api/categories/"
  }
  ```

## 笔记API

### 笔记列表与创建
- **URL**: `/api/notes/`
- **支持方法**: 
  - `GET`: 获取笔记列表
  - `POST`: 创建新笔记

#### GET 笔记列表
- **查询参数**:
  - `search`: 搜索关键词(标题和内容)
  - `category_id`: 按分类过滤
  - `ordering`: 排序字段，如`-updated_at`(降序)或`created_at`(升序)
  - `page`: 页码
  - `page_size`: 每页条数

- **成功响应**:
  ```json
  {
    "count": 100,
    "next": "http://127.0.0.1:8000/api/notes/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "title": "笔记标题",
        "content_preview": "笔记内容摘要...",
        "category": 1,
        "category_name": "工作",
        "created_at": "2023-05-01T12:00:00Z",
        "updated_at": "2023-05-01T12:00:00Z"
      },
      // ...更多笔记
    ]
  }
  ```

#### POST 创建笔记
- **请求体**:
  ```json
  {
    "title": "新笔记",
    "content": "这是新创建的笔记内容",
    "category": 1
  }
  ```

- **成功响应**:
  ```json
  {
    "id": 3,
    "title": "新笔记",
    "content": "这是新创建的笔记内容",
    "category": 1,
    "category_name": "工作",
    "created_at": "2023-05-03T15:30:00Z",
    "updated_at": "2023-05-03T15:30:00Z"
  }
  ```

### 笔记详情、更新与删除
- **URL**: `/api/notes/{id}/`
- **支持方法**: 
  - `GET`: 获取笔记详情
  - `PUT`: 全量更新笔记
  - `PATCH`: 部分更新笔记
  - `DELETE`: 硬删除笔记

#### GET 笔记详情
- **成功响应**:
  ```json
  {
    "id": 1,
    "title": "笔记标题",
    "content": "完整的笔记内容...",
    "category": 1,
    "category_name": "工作",
    "created_at": "2023-05-01T12:00:00Z",
    "updated_at": "2023-05-01T12:00:00Z"
  }
  ```

#### PUT/PATCH 更新笔记
- **请求体** (PATCH示例):
  ```json
  {
    "title": "更新后的标题"
  }
  ```

- **成功响应**:
  ```json
  {
    "id": 1,
    "title": "更新后的标题",
    "content": "完整的笔记内容...",
    "category": 1,
    "category_name": "工作",
    "created_at": "2023-05-01T12:00:00Z",
    "updated_at": "2023-05-03T16:45:00Z"
  }
  ```

### 软删除笔记
- **URL**: `/api/notes/{id}/soft_delete/`
- **方法**: `POST`
- **描述**: 软删除笔记(标记为已删除，不会真正从数据库删除)
- **成功响应**:
  ```json
  {
    "id": 1
  }
  ```

## 分类API

### 分类列表与创建
- **URL**: `/api/categories/`
- **支持方法**: 
  - `GET`: 获取分类列表
  - `POST`: 创建新分类

#### GET 分类列表
- **成功响应**:
  ```json
  {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "工作",
        "note_count": 5,
        "created_at": "2023-05-01T10:00:00Z"
      },
      {
        "id": 2,
        "name": "个人",
        "note_count": 3,
        "created_at": "2023-05-01T10:05:00Z"
      },
      // ...更多分类
    ]
  }
  ```

#### POST 创建分类
- **请求体**:
  ```json
  {
    "name": "新分类"
  }
  ```

- **成功响应**:
  ```json
  {
    "id": 3,
    "name": "新分类",
    "note_count": 0,
    "created_at": "2023-05-03T15:30:00Z"
  }
  ```

### 分类详情、更新与删除
- **URL**: `/api/categories/{id}/`
- **支持方法**: 
  - `GET`: 获取分类详情
  - `PUT`: 全量更新分类
  - `PATCH`: 部分更新分类
  - `DELETE`: 删除分类(如该分类下有笔记则不允许删除)

#### GET 分类详情
- **成功响应**:
  ```json
  {
    "id": 1,
    "name": "工作",
    "note_count": 5,
    "created_at": "2023-05-01T10:00:00Z"
  }
  ```

#### PUT/PATCH 更新分类
- **请求体**:
  ```json
  {
    "name": "更新后的分类名"
  }
  ```

- **成功响应**:
  ```json
  {
    "id": 1,
    "name": "更新后的分类名",
    "note_count": 5,
    "created_at": "2023-05-01T10:00:00Z"
  }
  ```

## 错误处理

### 常见错误响应

#### 400 Bad Request
```json
{
  "error": "该分类下有5条笔记，无法删除"
}
```

#### 404 Not Found
```json
{
  "detail": "未找到。"
}
```

## API过滤和排序示例

### 按关键词搜索笔记
```
GET /api/notes/?search=关键词
```

### 按分类过滤笔记
```
GET /api/notes/?category_id=1
```

### 按更新时间排序笔记
```
GET /api/notes/?ordering=-updated_at
```

### 组合使用
```
GET /api/notes/?search=关键词&category_id=1&ordering=-updated_at&page=2
```

## API浏览器界面
DRF提供了一个浏览器友好的API界面，方便开发和测试：

- 在浏览器中访问任何API URL，如`http://127.0.0.1:8000/api/notes/`
- 可以直接在界面中尝试API调用
- 提供了表单界面进行POST、PUT、PATCH请求 