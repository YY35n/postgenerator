import json
import random
import time
from post_generator import generate_post
from auto_post import post_to_discourse
from auto_respond import post_reply, get_first_post, search_topic_by_title
from reply_generator import generate_reply
from config import CATEGORY_ID, REPLY_DELAY_RANGE, KEYWORD


def load_accounts(path="accounts/accounts1.json"):
    with open(path, "r") as f:
        return json.load(f)

def choose_random_account(accounts):
    return random.choice(accounts)

if __name__ == "__main__":
    accounts = load_accounts()

    #随机选一个账号发帖
    author_account = choose_random_account(accounts)
    other_accounts = [account for account in accounts if account != author_account]

    print(f"使用 [{author_account['username']}] 发帖...")

    #生成主帖内容
    full_post = generate_post(KEYWORD)
    lines = full_post.strip().split("\n")
    title = lines[0].strip("# 标题：").strip()
    body = "\n".join(lines[1:]).strip()

    # 发帖
    post_to_discourse(title, body, author_account, CATEGORY_ID)

    #查找刚发的帖子的 topic_id
    time.sleep(5)
    topic_id = search_topic_by_title(title)
    if not topic_id:
        print(f"没找到刚才发的帖子：“{title}”")
        exit(1)

    print(f"成功创建主题帖 ID: {topic_id}")
    time.sleep(180)

    #其他账号依次回复
    for account in other_accounts:
        print(f"[{account['username']}] 正在回复...")
        context = get_first_post(topic_id)
        reply = generate_reply(context)
        post_reply(topic_id, reply, account["api_key"], account["username"])
        delay = random.randint(*REPLY_DELAY_RANGE)
        print(f"等待 {delay} 秒...")
        time.sleep(delay)

    print("所有账号已完成自动回复！")
