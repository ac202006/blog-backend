from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 环境变量（如果存在）

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 简单的文件存储
DATA_FILE = 'articles.json'

# PicGo 配置（可通过环境变量覆盖）
PICGO_API_URL = os.environ.get('PICGO_API_URL', 'https://www.picgo.net/api/1/upload')
PICGO_API_KEY = os.environ.get('PICGO_API_KEY')

def load_articles():
    """加载文章数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_articles(articles):
    """保存文章数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return {'message': '文章管理系统API正在运行'}

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """获取所有文章"""
    articles = load_articles()
    # 按创建时间倒序排列
    articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(articles)


@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """上传图片到 PicGo 图床并返回外链
    接收 form-data: image: <file>
    可选 query/body: filename 用于重命名
    """
    # 校验 API Key
    api_key = request.headers.get('X-API-Key') or PICGO_API_KEY
    if not api_key:
        return jsonify({'error': '缺少 PicGo API Key，请在请求头 X-API-Key 传入或设置环境变量 PICGO_API_KEY'}), 400

    if 'image' not in request.files:
        return jsonify({'error': '未找到文件字段: image'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    # 允许可选文件名
    filename_override = request.form.get('filename') or request.args.get('filename')
    file_tuple = (
        filename_override or file.filename,
        file.stream,
        file.mimetype or 'application/octet-stream'
    )

    try:
        # 转发到 PicGo
        headers = {
            'X-API-Key': api_key,
        }
        files = {
            'source': file_tuple
        }
        # 同时通过表单传递 key 与 format 以兼容 Chevereto 风格 API
        data = {
            'key': api_key,
            'format': 'json'
        }
        resp = requests.post(PICGO_API_URL, headers=headers, files=files, data=data, timeout=30)
        # 若 PicGo 有错误，尽量透传其响应体
        if not resp.ok:
            # 打印日志便于排查
            try:
                print(f"[PicGo Error] status={resp.status_code} body={resp.text[:500]}")
            except Exception:
                pass

            body = safe_json(resp)
            # 兼容 Chevereto: 400 且 error.code=101 表示重复上传
            try:
                if isinstance(body, dict):
                    err = body.get('error') or {}
                    err_code = err.get('code')
                    err_msg = (err.get('message') or '').lower()
                    if resp.status_code == 400 and (str(err_code) == '101' or 'duplicated' in err_msg):
                        img = body.get('image') or {}
                        # 若响应里包含已存在图片的信息，则当作成功返回
                        url = img.get('url') or img.get('display_url')
                        if url:
                            thumb = (img.get('thumb') or {}).get('url') if isinstance(img.get('thumb'), dict) else img.get('display_url')
                            medium = (img.get('medium') or {}).get('url') if isinstance(img.get('medium'), dict) else None
                            return jsonify({
                                'url': url,
                                'display_url': img.get('display_url') or url,
                                'thumb_url': thumb,
                                'medium_url': medium,
                                'id': img.get('id_encoded') or img.get('filename'),
                                'width': img.get('width'),
                                'height': img.get('height'),
                                'size': img.get('size'),
                                'mime': img.get('mime'),
                                'note': 'duplicate_reused'
                            }), 200
                        # 无 URL 则返回 409 冲突，明确重复
                        return jsonify({'error': '图片已存在（重复上传）', 'code': 101}), 409
            except Exception:
                # 忽略解析错误，走通用兜底
                pass

            return jsonify({'error': 'PicGo 上传失败', 'status_code': resp.status_code, 'body': body}), 502

        data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else None
        if not data:
            return jsonify({'error': 'PicGo 响应非 JSON', 'raw': resp.text[:1000]}), 502

        # 期望结构：{"status_code":200, "image": { "url": ..., "display_url": ... }}
        image = data.get('image') or {}
        url = image.get('url') or image.get('display_url')
        thumb = (image.get('thumb') or {}).get('url') if isinstance(image.get('thumb'), dict) else image.get('display_url')
        medium = (image.get('medium') or {}).get('url') if isinstance(image.get('medium'), dict) else None

        if not url:
            return jsonify({'error': '未在 PicGo 响应中找到图片 URL', 'picgo_response': data}), 502

        return jsonify({
            'url': url,
            'display_url': image.get('display_url') or url,
            'thumb_url': thumb,
            'medium_url': medium,
            'id': image.get('id_encoded') or image.get('filename'),
            'width': image.get('width'),
            'height': image.get('height'),
            'size': image.get('size'),
            'mime': image.get('mime')
        }), 200

    except requests.Timeout:
        return jsonify({'error': 'PicGo 请求超时'}), 504
    except requests.RequestException as e:
        return jsonify({'error': 'PicGo 请求异常', 'detail': str(e)}), 502


def safe_json(resp):
    """尽力解析 JSON，否则返回文本摘要"""
    try:
        return resp.json()
    except Exception:
        return resp.text[:1000]

@app.route('/api/articles', methods=['POST'])
def create_article():
    """创建新文章"""
    data = request.get_json()
    
    articles = load_articles()
    
    # 从content中提取标题（第一行作为标题）
    content = data.get('content', '')
    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else '无标题'
    
    # 生成摘要（前100个字符）
    summary = content.replace('#', '').replace('*', '').strip()[:100]
    if len(summary) == 100:
        summary += '...'
    
    # 创建新文章
    new_article = {
        'id': len(articles) + 1,
        'title': title,
        'content': content,
        'summary': summary,
        'author': data.get('author', 'AC_101_'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'view_count': 0
    }
    
    articles.append(new_article)
    save_articles(articles)
    
    return jsonify(new_article), 201

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """获取单篇文章"""
    articles = load_articles()
    
    for i, article in enumerate(articles):
        if article['id'] == article_id:
            article['view_count'] += 1  # 增加浏览量
            articles[i] = article
            save_articles(articles)
            return jsonify(article)
    
    return jsonify({'error': '文章不存在'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)