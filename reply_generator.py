from openai import OpenAI
from config import DEEPSEEK_API_KEY
client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url="https://api.deepseek.com")

def generate_reply(context):
    prompt = f"请作为一个这个论坛用户自然,友善地回复以下帖子内容，口吻更像真人回复，尽量简洁，使用类似于一亩三分地用户的口吻：\n\n{context}"
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[{"role": "user", "content": prompt}],
        temperature=1.2
    )
    return response.choices[0].message.content
