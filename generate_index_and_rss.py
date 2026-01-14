import os
import random
import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup

# ランダムなカラーパレット
COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFBE0B', '#FB5607',
    '#8338EC', '#3A86FF', '#FF006E', '#A5DD9B', '#F9C74F'
]

# HTMLテンプレート
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>誤字ロマの道具箱</title>
    <style>
        body {{
            font-family: "Yu Mincho", "Hiragino Mincho Pro", serif;
            margin: 20px;
            background-color: {}1A;
            transition: background-color 0.5s;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            text-align: center;
            color: #333;
            font-family: "Yu Mincho", "Hiragino Mincho Pro", serif;
            margin-bottom: 20px;
        }}
        #search {{
            max-width: 600px;
            width: 100%;
            padding: 10px;
            font-family: "Yu Mincho", "Hiragino Mincho Pro", serif;
            font-size: 16px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }}
        #fileList {{
            width: 100%;
            max-width: 600px;
            padding: 0;
            margin: 0 auto;
        }}
        #fileList li {{
            padding: 10px;
            margin: 5px 0;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: background-color 0.3s;
            display: none;
            list-style-type: none;
            position: relative;
        }}
        #fileList li.visible {{
            display: block;
        }}
        #fileList li:hover {{
            background-color: #e9e9e9;
        }}
        #fileList a {{
            text-decoration: none;
            color: inherit;
            display: block;
        }}
        .date {{
            position: absolute;
            top: 5px;
            right: 10px;
            font-size: 0.8em;
            color: #999;
        }}
        .description {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .rss-link {{
            text-align: center;
            margin-top: 20px;
            width: 100%;
            max-width: 600px;
        }}
    </style>
</head>
<body>
    <h1>誤字ロマの道具箱</h1>
    <input type="text" id="search" placeholder="検索..." autofocus>
    <ul id="fileList">
        {}
    </ul>
    <div class="rss-link">
        <a href="rss.xml" target="_blank">RSSフィード</a>
    </div>
    <script>
        // 初期表示で全項目を表示
        document.querySelectorAll('#fileList li').forEach(item => {{
            item.classList.add('visible');
        }});

        // 検索機能
        document.getElementById('search').addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();
            const items = document.querySelectorAll('#fileList li');
            let visibleCount = 0;
            let lastVisibleItem = null;

            items.forEach(item => {{
                const text = item.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                item.classList.toggle('visible', isVisible);
                if (isVisible) {{
                    visibleCount++;
                    lastVisibleItem = item;
                }}
            }});

            // 検索結果が1つだけの場合はそのページを開く
            if (visibleCount === 1 && searchTerm.length > 0) {{
                window.open(lastVisibleItem.querySelector('a').href, '_blank');
            }}
        }});
    </script>
</body>
</html>
"""

# RSSテンプレート
RSS_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
    <channel>
        <title>誤字ロマの道具箱</title>
        <link>https://tools.poet.blue/</link>
        <description>生活を楽しくする小物たちを公開</description>
        <lastBuildDate>{}</lastBuildDate>
        {}
    </channel>
</rss>
"""

# RSSアイテムテンプレート
RSS_ITEM_TEMPLATE = """
        <item>
            <title>{}</title>
            <link>{}</link>
            <pubDate>{}</pubDate>
            <description>{}</description>
        </item>
"""

def get_html_files():
    """現在のディレクトリ内のHTMLファイルを取得（index.htmlを除く）"""
    files = []
    for file in os.listdir('.'):
        if file.endswith('.html') and file != 'index.html':
            base_name = os.path.splitext(file)[0]
            date, description = get_meta_info(file)
            files.append((file, base_name, date, description))
    return sorted(files, key=lambda x: x[1])

def get_meta_info(filename):
    """HTMLファイルからmeta dateとmeta descriptionを取得"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            meta_date = soup.find('meta', attrs={'name': 'date'})
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            date = meta_date['content'] if meta_date else format_date(os.path.getctime(filename))
            description = meta_desc['content'] if meta_desc else '説明文がありません。'
            return date, description
    except Exception:
        return format_date(os.path.getctime(filename)), '説明文がありません。'

def format_date(date_str):
    """YYYY-MM-DD形式の文字列をRSS用の形式に変換"""
    try:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%a, %d %b %Y %H:%M:%S +0900')
    except ValueError:
        return datetime.datetime.fromtimestamp(os.path.getctime(date_str)).strftime('%a, %d %b %Y %H:%M:%S +0900')

def generate_html_and_rss():
    """index.htmlとrss.xmlを生成"""
    files = get_html_files()
    if not files:
        print("HTMLファイルが見つかりませんでした。")
        return

    # 背景色をランダムに選択
    bg_color = random.choice(COLORS)

    # HTMLリストアイテム生成
    html_items = []
    rss_items = []
    now = datetime.datetime.now()

    for file, base_name, date, description in files:
        display_date = date.replace('-', '/')
        pub_date = format_date(date)
        html_items.append(
            f'<li><div class="date">{display_date}</div><a href="{file}">{base_name}</a><div class="description">{description}</div></li>'
        )
        rss_items.append(RSS_ITEM_TEMPLATE.format(base_name, file, pub_date, description))

    # HTML生成
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE.format(bg_color, '\n        '.join(html_items)))
    print("index.html を生成しました。")

    # RSS生成
    rss_content = RSS_TEMPLATE.format(
        now.strftime('%a, %d %b %Y %H:%M:%S +0900'),
        '\n'.join(rss_items)
    )
    rss_pretty = minidom.parseString(rss_content).toprettyxml(indent='    ')
    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss_pretty)
    print("rss.xml を生成しました。")

if __name__ == '__main__':
    generate_html_and_rss()
