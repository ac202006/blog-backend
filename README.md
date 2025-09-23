# 文章管理系统 - 后端API

基于Flask的轻量级文章管理后端，提供RESTful API接口。

## 项目结构

```
backend/
├── app.py                 # 主应用文件
├── requirements.txt       # Python依赖
├── start-backend.sh      # 启动脚本
├── articles.json         # 文章数据文件（自动生成）
└── README.md             # 本文件
```

## 功能特性

- 🚀 **轻量级**: 基于Flask，简单易用
- 💾 **文件存储**: 使用JSON文件存储，无需配置数据库
- 🔄 **RESTful API**: 标准的REST接口设计
- 🌐 **跨域支持**: 内置CORS支持
- 📝 **文章管理**: 完整的文章CRUD操作

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

### 获取单篇文章
```http
GET /api/articles/{id}
```

**路径参数：**
- `id`: 文章ID

**响应：** 返回文章对象，同时增加浏览量

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

### 数据存储
- 文章数据存储在 `articles.json` 文件中
- 首次运行时会自动创建该文件
- 数据格式为JSON数组

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
chmod +x start-backend.sh
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