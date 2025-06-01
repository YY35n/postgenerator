import os
import re
import time
import json
import requests
import faiss
import numpy as np
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

BASE_URL = "https://www.1point3acres.com/bbs/"
FORUM_ID = 28  # forum-28 开头的版块
START_PAGE = 1
END_PAGE = 5   # ✅ 想爬多少页自己改，比如到 forum-28-5.html
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.1point3acres.com/bbs/forum-28-1.html"
}

# 广告提示清单
AD_PATTERNS = [
    r'^注册一亩三分地论坛.*?注册账号x',
    r'^This post was last edited.*?on \d{4}-\d{1,2}-\d{1,2}',
    r'^您需要登录才可以下载或查看附件。没有帐号？注册账号x',
]

def clean_text(text):
    """移除开头的广告段落"""
    for pattern in AD_PATTERNS:
        text = re.sub(pattern, '', text)
    return text.strip()

def get_threads_from_forum(forum_url):
    """正确抓取每个帖子标题和链接"""
    res = requests.get(forum_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    threads = []
    for tbody in soup.find_all('tbody', id=lambda x: x and x.startswith('normalthread_')):
        a_tag = tbody.select_one('th a.s.xst')
        if a_tag:
            title = a_tag.get_text(strip=True)
            link = BASE_URL + a_tag['href']
            threads.append({'title': title, 'link': link})
    return threads



# ✅ 主流程开始
new_data = []

for page_num in range(START_PAGE, END_PAGE + 1):
    forum_url = f"{BASE_URL}forum-{FORUM_ID}-{page_num}.html"
    print(f"\n🌐 正在抓取第 {page_num} 页：{forum_url}")
    threads = get_threads_from_forum(forum_url)
    print(f"  找到 {len(threads)} 个帖子")

    for idx, thread in enumerate(threads, 1):
        print(f"    [{idx}/{len(threads)}] 抓取: {thread['title']}")
        content = get_threads_from_forum(thread['link'])
        new_data.append({
            'title': thread['title'],
            'link': thread['link'],
            'content': content or "（未能获取主贴内容）"
        })
        time.sleep(1)

# ✅ 合并旧数据
if os.path.exists("threads_cleaned.json"):
    with open("threads_cleaned.json", "r", encoding='utf-8') as f:
        old_data = json.load(f)
    all_data = old_data + new_data
else:
    all_data = new_data

# 保存JSON
with open("threads_cleaned.json", "w", encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 当前总共 {len(all_data)} 条帖子，已保存到 threads_cleaned.json")

# ✅ 嵌入并增量保存 FAISS
print("✨ 正在将新增帖子转化为向量并合并到FAISS数据库...")

# 加载嵌入模型
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# 文本组合（新抓到的）
new_texts = [f"{item['title']}。\n{item['content']}" for item in new_data]
new_embeddings = embed_model.encode(new_texts, show_progress_bar=True)

# 处理FAISS
if os.path.exists("forum_posts_index.faiss") and os.path.exists("forum_posts_texts.json"):
    print("🔄 检测到已有旧数据库，正在增量合并...")
    index = faiss.read_index("forum_posts_index.faiss")
    with open("forum_posts_texts.json", "r", encoding='utf-8') as f:
        old_texts = json.load(f)
    all_texts = old_texts + new_texts
else:
    print("🆕 没有旧数据库，新建...")
    dimension = new_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    all_texts = new_texts

index.add(np.array(new_embeddings))

# 保存
faiss.write_index(index, "forum_posts_index.faiss")
with open("forum_posts_texts.json", "w", encoding='utf-8') as f:
    json.dump(all_texts, f, ensure_ascii=False, indent=2)

print(f"\n✅ 当前总共 {len(all_texts)} 条文本，向量库已更新完成！")
