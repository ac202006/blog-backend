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
    """上传图片到 PicGo 图床并返回外链"""
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
        # 上传到 PicGo
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

        return jsonify({
            'url': url,
            'display_url': url,
            'id': image.get('id_encoded'),
            'width': image.get('width'),
            'height': image.get('height'),
            'size': image.get('size')
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)