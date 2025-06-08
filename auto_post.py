import requests
import json
import random
from config import DISCOURSE_URL

#加载账号
def accountDecider(website):
    if website == 1:
        return 'accounts1.json'
    elif website == 2:
        return 'accounts2.json'
    else:
        return 'accounts3.json'

def load_accounts(path):
    with open(path, "r") as f:
        return json.load(f)

#随机抽选
def choose_random_account(accounts):
    return random.choice(accounts)

#发帖
def post_to_discourse(title, content, account, CATEGORY_ID):
    url = f"{DISCOURSE_URL}/posts.json"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Api-Key": account["api_key"],
        "Api-Username": account["username"]
    }
    payload = {
        "title": title,
        "raw": content,
        "category": CATEGORY_ID
    }
    response = requests.post(url, headers=headers, data=payload, verify=False)
    
    if response.status_code == 200:
        print(f"成功由 [{account['username']}] 发帖：{title}")
    else:
        print(f"发帖失败 [{account['username']}]", response.status_code)
        print(response.text)
