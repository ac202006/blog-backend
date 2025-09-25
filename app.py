from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import hashlib
from datetime import datetime
import requests
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()  # 加载 .env 环境变量（如果存在）

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 简单的文件存储
DATA_FILE = 'articles.json'
IMAGES_FILE = 'images.json'

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

def load_images():
    """加载图片数据"""
    if os.path.exists(IMAGES_FILE):
        with open(IMAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_images(images):
    """保存图片数据"""
    with open(IMAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=2)

def calculate_image_hash(file_data):
    """计算图片的MD5哈希值"""
    try:
        # 重置文件指针到开始位置
        file_data.seek(0)
        # 计算文件内容的MD5哈希
        hasher = hashlib.md5()
        for chunk in iter(lambda: file_data.read(4096), b""):
            hasher.update(chunk)
        file_data.seek(0)  # 重置文件指针供后续使用
        return hasher.hexdigest()
    except Exception as e:
        print(f"计算图片哈希失败: {e}")
        return None

def find_duplicate_image(image_hash):
    """查找是否已存在相同哈希的图片"""
    images = load_images()
    for image in images:
        if image.get('hash') == image_hash:
            return image
    return None

def save_image_record(image_hash, url, filename, size=None, width=None, height=None):
    """保存图片记录"""
    images = load_images()
    new_image = {
        'hash': image_hash,
        'url': url,
        'filename': filename,
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'size': size,
        'width': width,
        'height': height
    }
    images.append(new_image)
    save_images(images)
    return new_image

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
    """上传图片到 PicGo 图床并返回外链，支持重复图片检测"""
    # 校验 API Key
    api_key = request.headers.get('X-API-Key') or PICGO_API_KEY
    if not api_key:
        return jsonify({'error': '缺少 PicGo API Key'}), 400

    if 'image' not in request.files:
        return jsonify({'error': '未找到文件字段: image'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    try:
        # 计算图片哈希值
        image_hash = calculate_image_hash(file.stream)
        if not image_hash:
            return jsonify({'error': '计算图片哈希失败'}), 500
        
        # 检查是否已存在相同图片
        existing_image = find_duplicate_image(image_hash)
        if existing_image:
            return jsonify({
                'url': existing_image['url'],
                'display_url': existing_image['url'],
                'id': existing_image.get('id'),
                'width': existing_image.get('width'),
                'height': existing_image.get('height'),
                'size': existing_image.get('size'),
                'duplicate': True,
                'message': '检测到重复图片，返回已有URL',
                'upload_time': existing_image.get('upload_time')
            }), 200
        
        # 如果不是重复图片，上传到 PicGo
        file.stream.seek(0)  # 重置文件指针
        files = {'source': file}
        data = {'key': api_key, 'format': 'json'}
        headers = {'X-API-Key': api_key}
        
        resp = requests.post(PICGO_API_URL, headers=headers, files=files, data=data, timeout=30)
        
        if not resp.ok:
            return jsonify({'error': 'PicGo 上传失败', 'status': resp.status_code}), 502

        result = resp.json()
        image = result.get('image', {})
        url = image.get('url') or image.get('display_url')

        if not url:
            return jsonify({'error': '未获取到图片URL'}), 502

        # 保存图片记录
        image_record = save_image_record(
            image_hash=image_hash,
            url=url,
            filename=file.filename,
            size=image.get('size'),
            width=image.get('width'),
            height=image.get('height')
        )

        return jsonify({
            'url': url,
            'display_url': url,
            'id': image.get('id_encoded'),
            'width': image.get('width'),
            'height': image.get('height'),
            'size': image.get('size'),
            'duplicate': False,
            'message': '图片上传成功',
            'hash': image_hash,
            'upload_time': image_record.get('upload_time')
        }), 200

    except requests.Timeout:
        return jsonify({'error': 'PicGo 请求超时'}), 504
    except requests.RequestException as e:
        return jsonify({'error': 'PicGo 请求异常', 'detail': str(e)}), 502
    except Exception as e:
        return jsonify({'error': '上传失败', 'detail': str(e)}), 500

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

@app.route('/api/images', methods=['GET'])
def get_images():
    """获取所有已上传的图片记录"""
    images = load_images()
    # 按上传时间倒序排列
    images.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    return jsonify(images)

@app.route('/api/images/stats', methods=['GET'])
def get_image_stats():
    """获取图片统计信息"""
    images = load_images()
    total_images = len(images)
    
    # 计算总大小（如果有的话）
    total_size = 0
    for image in images:
        size = image.get('size')
        if size and isinstance(size, (int, float)):
            total_size += size
    
    return jsonify({
        'total_images': total_images,
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size > 0 else 0
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)