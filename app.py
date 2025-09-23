from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 简单的文件存储
DATA_FILE = 'articles.json'

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