import requests
import random
import time
from reply_generator import generate_reply
from config import DISCOURSE_URL, REPLY_DELAY_RANGE

#搜索文章
def search_topic_by_title(title):
    url = f"{DISCOURSE_URL}/search/query.json?term={title}"
    response = requests.get(url)
    results = response.json()
    topics = results.get("topics", [])
    for topic in topics:
        if title in topic.get("fancy_title", ""):
            return topic["id"]
    return None

#根据ID搜post
def get_first_post(topic_id):
    url = f"{DISCOURSE_URL}/t/{topic_id}.json"
    response = requests.get(url)
    posts = response.json()["post_stream"]["posts"]
    return posts[0]["cooked"] if posts else ""


def post_reply(topic_id, reply_text, api_key, username):
    url = f"{DISCOURSE_URL}/posts.json"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Api-Key": api_key,
        "Api-Username": username
    }
    payload = {
        "topic_id": topic_id,
        "raw": reply_text
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        print(f"[{username}] 成功回复到帖子 ID {topic_id}")
    else:
        print(f"[{username}] 回复失败：", response.status_code, response.text)

def auto_reply_to_topic(title, accounts):
    topic_id = search_topic_by_title(title)
    if not topic_id:
        print(f"找不到标题包含“{title}”的帖子")
        return

    print(f"找到帖子 ID: {topic_id}")
    context = get_first_post(topic_id)

    for account in accounts:
        print(f"使用账号 {account['username']} 回复中...")
        reply = generate_reply(context)
        post_reply(topic_id, reply, account["api_key"], account["username"])
        delay = random.randint(*REPLY_DELAY_RANGE)
        print(f"等待 {delay} 秒后...")
        time.sleep(delay)

