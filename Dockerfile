# 二开推荐阅读[如何提高项目构建效率](https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/build/speed.html)
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能体积小）。
FROM alpine:3.13

# 设置时区为上海时间
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 使用腾讯云镜像源，安装基本依赖
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
    && apk update \
    && apk add --no-cache \
        python3 \
        py3-pip \
        # 添加编译工具
        gcc \
        musl-dev \
        python3-dev \
        # 添加加密库依赖
        libffi-dev \
        openssl-dev \
        # 添加预编译的Python包
        py3-cryptography \
        py3-cffi \
        py3-boto3 \
    && rm -rf /var/cache/apk/*

# 创建并设置工作目录
WORKDIR /app

# 先复制并安装依赖，利用Docker缓存
COPY requirements.txt /app/
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# 复制项目文件
COPY . /app/

# 收集静态文件(如有需要)
# RUN python3 manage.py collectstatic --noinput

# 执行数据库迁移(如有需要)
# RUN python3 manage.py migrate

# 暴露端口
EXPOSE 80

# 启动服务
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
