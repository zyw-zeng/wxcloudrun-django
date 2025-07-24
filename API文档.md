# 笔记应用 API 文档

## 概述
本文档描述了笔记应用的后端 API 接口，包括笔记和分类的基本操作。

## 基本信息
- **基础 URL**: `http://127.0.0.1:8000`
- **响应格式**: 所有 API 返回 JSON 格式数据
- **标准响应结构**:
  ```json
  {
    "code": 0,         // 0表示成功，非0表示失败
    "data": {},        // 响应数据，成功时返回
    "errorMsg": ""     // 错误信息，失败时返回
  }
  ```

## 笔记接口

### 1. 获取笔记列表
获取所有未删除的笔记列表，支持分页、分类筛选和关键词搜索。

- **URL**: `/api/note/list`
- **方法**: `GET`
- **参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页条数，默认为10
  - `category_id`: 分类ID，可选
  - `keyword`: 搜索关键词，可选

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "total": 100,
      "page": 1,
      "page_size": 10,
      "list": [
        {
          "id": 1,
          "title": "笔记标题",
          "content": "笔记内容摘要...",
          "category_id": 1,
          "category_name": "工作",
          "created_at": "2023-05-01 12:00:00",
          "updated_at": "2023-05-01 12:00:00"
        }
        // ...更多笔记
      ]
    }
  }
  ```

### 2. 创建笔记
创建一条新的笔记。

- **URL**: `/api/note/create`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "title": "笔记标题",
    "content": "笔记内容",
    "category_id": 1  // 可选
  }
  ```

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1,
      "title": "笔记标题",
      "content": "笔记内容",
      "category_id": 1,
      "created_at": "2023-05-01 12:00:00",
      "updated_at": "2023-05-01 12:00:00"
    }
  }
  ```

### 3. 更新笔记
更新指定ID的笔记内容。

- **URL**: `/api/note/update/{note_id}`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "title": "更新后的标题",  // 可选
    "content": "更新后的内容", // 可选
    "category_id": 2  // 可选，null表示无分类
  }
  ```

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1,
      "title": "更新后的标题",
      "content": "更新后的内容",
      "category_id": 2,
      "category_name": "个人",
      "created_at": "2023-05-01 12:00:00",
      "updated_at": "2023-05-02 14:30:00"
    }
  }
  ```

### 4. 删除笔记
软删除指定ID的笔记（标记为已删除）。

- **URL**: `/api/note/delete/{note_id}`
- **方法**: `POST`
- **请求体**: 无需请求体

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1
    }
  }
  ```

### 5. 获取笔记详情
获取指定ID笔记的完整信息。

- **URL**: `/api/note/detail/{note_id}`
- **方法**: `GET`
- **参数**: 无需额外参数

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 1,
      "title": "笔记标题",
      "content": "笔记完整内容...",
      "category_id": 1,
      "category_name": "工作",
      "created_at": "2023-05-01 12:00:00",
      "updated_at": "2023-05-01 12:00:00"
    }
  }
  ```

## 分类接口

### 1. 获取分类列表
获取所有分类及其包含的笔记数量。

- **URL**: `/api/category/list`
- **方法**: `GET`
- **参数**: 无需参数

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": [
      {
        "id": 1,
        "name": "工作",
        "note_count": 5,
        "created_at": "2023-05-01 10:00:00"
      },
      {
        "id": 2,
        "name": "个人",
        "note_count": 3,
        "created_at": "2023-05-01 10:05:00"
      }
      // ...更多分类
    ]
  }
  ```

### 2. 创建分类
创建一个新的笔记分类。

- **URL**: `/api/category/create`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "name": "新分类名称"
  }
  ```

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 3,
      "name": "新分类名称",
      "created_at": "2023-05-03 09:15:00"
    }
  }
  ```

### 3. 更新分类
更新指定ID的分类信息。

- **URL**: `/api/category/update/{category_id}`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "name": "更新后的分类名称"
  }
  ```

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 3,
      "name": "更新后的分类名称",
      "created_at": "2023-05-03 09:15:00"
    }
  }
  ```

### 4. 删除分类
删除指定ID的分类，前提是该分类下没有笔记。

- **URL**: `/api/category/delete/{category_id}`
- **方法**: `POST`
- **请求体**: 无需请求体

- **成功响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": 3
    }
  }
  ```

## 错误码说明

- **0**: 成功
- **-1**: 一般错误，详见errorMsg字段

## 常见错误响应

```json
{
  "code": -1,
  "errorMsg": "笔记不存在"
}
```

```json
{
  "code": -1,
  "errorMsg": "标题不能为空"
}
```

```json
{
  "code": -1,
  "errorMsg": "分类名称已存在"
}
```

```json
{
  "code": -1,
  "errorMsg": "该分类下有笔记，无法删除"
}
``` 