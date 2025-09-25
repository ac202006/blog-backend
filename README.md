# 文章管理系统 - 后端API

基于Flask的轻量级文章管理后端，提供RESTful API接口。

## 项目结构

```
blog-backend/
├── app.py                 # 主应用文件
├── requirements.txt       # Python依赖
├── start.sh              # 启动脚本
├── articles.json         # 文章数据文件（自动生成）
├── docker-compose.yml    # Docker Compose配置
├── Dockerfile            # Docker镜像配置
├── .env.example          # 环境变量示例
└── README.md             # 本文件
```

## 功能特性

- 🚀 **轻量级**: 基于Flask，简单易用
- 💾 **文件存储**: 使用JSON文件存储，无需配置数据库
- 🔄 **RESTful API**: 标准的REST接口设计
- 🌐 **跨域支持**: 内置CORS支持
- 📝 **文章管理**: 完整的文章CRUD操作
- 🖼️ **PicGo图床**: 集成PicGo图床服务，轻松上传图片
- 🔍 **图片去重**: 自动检测重复图片，避免重复上传，直接返回已有URL
- 📊 **图片统计**: 提供图片上传统计和管理功能

## 快速开始

### 1. 安装依赖

```bash
# 自动安装（推荐）
./start-backend.sh

# 手动安装
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 使用启动脚本
./start-backend.sh

# 手动启动
python app.py
```

服务将运行在 `http://localhost:8000`

## API接口文档

### 获取所有文章
```http
GET /api/articles
```

**响应示例：**
```json
[
  {
    "id": 1,
    "title": "文章标题",
    "content": "# 文章标题\n\n文章内容...",
    "summary": "文章摘要...",
    "author": "AC_101_",
    "created_at": "2024-01-01 12:00:00",
    "view_count": 5
  }
]
```

### 创建新文章
```http
POST /api/articles
Content-Type: application/json
```

**请求体：**
```json
{
  "content": "# 文章标题\n\n文章内容...",
  "author": "作者名称"
}
```

**响应：** 返回创建的文章对象（状态码：201）

### 上传图片到PicGo图床
```http
POST /api/upload/image
Content-Type: multipart/form-data
```

**请求头（可选）：**
- `X-API-Key`: PicGo API Key（未设置环境变量时必需）

**表单字段：**
- `image`: 图片文件

**响应示例（新图片上传）：**
```json
{
  "url": "https://origin.picgo.net/2025/09/25/xxx.png",
  "display_url": "https://origin.picgo.net/2025/09/25/xxx.png",
  "id": "03JQsr",
  "width": 848,
  "height": 848,
  "size": 783728,
  "duplicate": false,
  "message": "图片上传成功",
  "hash": "a1b2c3d4e5f6...",
  "upload_time": "2025-09-25 14:30:00"
}
```

**响应示例（检测到重复图片）：**
```json
{
  "url": "https://origin.picgo.net/2025/09/25/xxx.png",
  "display_url": "https://origin.picgo.net/2025/09/25/xxx.png",
  "id": "03JQsr",
  "width": 848,
  "height": 848,
  "size": 783728,
  "duplicate": true,
  "message": "检测到重复图片，返回已有URL",
  "upload_time": "2025-09-25 14:25:00"
}
```

### 获取单篇文章
```http
GET /api/articles/{id}
```

**路径参数：**
- `id`: 文章ID

**响应：** 返回文章对象，同时增加浏览量

### 获取已上传图片列表
```http
GET /api/images
```

**响应：** 返回所有已上传图片的记录列表（按上传时间倒序）

**响应示例：**
```json
[
  {
    "hash": "a1b2c3d4e5f6...",
    "url": "https://origin.picgo.net/2025/09/25/xxx.png",
    "filename": "test.png",
    "upload_time": "2025-09-25 14:30:00",
    "size": 783728,
    "width": 848,
    "height": 848
  }
]
```

### 获取图片统计信息
```http
GET /api/images/stats
```

**响应：**
```json
{
  "total_images": 5,
  "total_size": 2048000,
  "total_size_mb": 1.95
}
```

### 检查服务状态
```http
GET /
```

**响应：**
```json
{
  "message": "文章管理系统API正在运行"
}
```

## 数据结构

### 文章对象
```json
{
  "id": "唯一标识符",
  "title": "文章标题（从content第一行提取）",
  "content": "完整的Markdown内容",
  "summary": "自动生成的摘要（前100字符）",
  "author": "作者名称",
  "created_at": "创建时间（YYYY-MM-DD HH:MM:SS）",
  "view_count": "浏览次数"
}
```

## 技术栈

- **Python 3.7+**: 编程语言
- **Flask 2.3.2**: Web框架
- **Flask-CORS 4.0.0**: 跨域支持
- **JSON**: 数据存储格式

## 配置说明

### 环境变量
- `HOST`: 服务器地址（默认：0.0.0.0）
- `PORT`: 服务器端口（默认：8000）
- `DEBUG`: 调试模式（默认：True）
- `PICGO_API_URL`: PicGo API 上传地址（默认：`https://www.picgo.net/api/1/upload`）
- `PICGO_API_KEY`: PicGo API Key（可选；若不设置，调用时必须通过请求头 `X-API-Key` 提供）

### 数据存储
- 文章数据存储在 `articles.json` 文件中
- 图片记录存储在 `images.json` 文件中  
- 首次运行时会自动创建这些文件
- 数据格式为JSON数组

## 图片去重功能

### 工作原理
1. **哈希计算**: 上传图片时，系统会计算图片内容的MD5哈希值
2. **重复检测**: 检查该哈希值是否已存在于图片记录中
3. **智能响应**: 
   - 如果是重复图片，直接返回已有的URL，避免重复上传
   - 如果是新图片，正常上传到PicGo并保存记录

### 特性优势
- ⚡ **节省带宽**: 避免重复上传相同图片
- 💾 **节省存储**: 减少图床存储空间占用
- 🚀 **提升速度**: 重复图片直接返回URL，响应更快
- 📊 **统计管理**: 记录所有图片信息，便于管理

### 数据结构
图片记录包含以下信息：
```json
{
  "hash": "图片内容的MD5哈希值",
  "url": "图片在图床的URL",
  "filename": "原始文件名",
  "upload_time": "首次上传时间",
  "size": "文件大小（字节）",
  "width": "图片宽度",
  "height": "图片高度"
}
```

## 开发说明

### 添加新功能
1. 在 `app.py` 中定义新的路由
2. 实现对应的处理函数
3. 更新API文档

### 数据库迁移
如需使用数据库替代JSON文件存储：
1. 安装数据库驱动（如 `psycopg2-binary` 用于PostgreSQL）
2. 修改 `load_articles()` 和 `save_articles()` 函数
3. 添加数据库连接配置

## 部署建议

### 开发环境
```bash
python app.py
```

### 生产环境
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# 使用uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:8000 --wsgi-file app.py --callable app
```

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PICGO_API_URL=https://www.picgo.net/api/1/upload
# ENV PICGO_API_KEY=your_key_here
EXPOSE 8000
CMD ["python", "app.py"]
```

## 故障排除

### 端口占用
```bash
# 查看端口占用
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

### 权限问题
```bash
# 给启动脚本执行权限
chmod +x start.sh
```

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 安全注意事项

⚠️ **重要**: 本后端仅用于开发和测试环境，生产环境需要额外的安全措施：

1. **身份验证**: 添加用户认证和授权机制
2. **输入验证**: 严格验证和清理用户输入
3. **HTTPS**: 使用SSL/TLS加密通信
4. **防火墙**: 限制不必要的端口访问
5. **备份**: 定期备份数据文件

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或Pull Request。

---

### 快速测试 PicGo 上传

1) 启动后端：
```bash
./start.sh
```

2) 本地测试：
```bash
curl -F "image=@test.png" http://localhost:8000/api/upload/image
```

3) 携带 PicGo Key（如果未在环境变量中配置）：
```bash
curl -H "X-API-Key: <你的PicGoKey>" -F "image=@test.png" http://localhost:8000/api/upload/image
```

## 使用 Docker 运行

本项目已提供 `Dockerfile` 与 `docker-compose.yml`，可直接容器化运行。

### 直接使用 Docker

```bash
# 在项目根目录
docker build -t blog-backend:latest .
docker run --name blog-backend -p 8000:8000 blog-backend:latest
# 停止并清理
# docker rm -f blog-backend
```

### 使用 Docker Compose

```bash
docker compose up --build -d
docker compose logs -f
# 关闭
# docker compose down
```

服务默认监听 0.0.0.0:8000（见 `app.py`），可以通过环境变量 `PORT` 覆盖容器内部端口（记得同步修改端口映射）。

### 数据持久化

`docker-compose.yml` 已将以下路径挂载到宿主机，容器重建后仍可保留：
- `./articles.json:/app/articles.json` 用于文章数据文件

**注意：** 图片文件通过PicGo上传到外部图床，不再需要本地存储。

### 生产部署建议

建议使用 Gunicorn 作为 WSGI 服务器运行 Flask 应用：

```dockerfile
# 在 Dockerfile 中将 CMD 改为：
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
```

或在运行容器时覆盖：

```bash
docker run --name blog-backend -p 8000:8000 blog-backend:latest \
  gunicorn -b 0.0.0.0:8000 app:app
```

### 本机开发脚本

`start.sh` 仍用于本机非容器化开发（创建并激活虚拟环境、安装依赖、运行 Flask）。容器内无需创建虚拟环境。