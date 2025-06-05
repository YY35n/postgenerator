# post_generator.py
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from config import DEEPSEEK_API_KEY

# ==== 设置向量库路径 ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_PATH = os.path.join(BASE_DIR, 'mitbbs', 'forum_posts_index.faiss')
TEXT_PATH = os.path.join(BASE_DIR, 'mitbbs', 'forum_posts_texts.json')

class PostGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')

        # 载入 FAISS 向量库
        if not os.path.exists(FAISS_PATH):
            raise FileNotFoundError(f"未找到向量库文件: {FAISS_PATH}")
        if not os.path.exists(TEXT_PATH):
            raise FileNotFoundError(f"未找到文本文件: {TEXT_PATH}")
        
        self.index = faiss.read_index(FAISS_PATH)
        with open(TEXT_PATH, 'r', encoding='utf-8') as f:
            self.texts = json.load(f)

    def clean_content(self, text):
        if not text:
            return ""
        text = ' '.join(text.split())  # 去除多余空格
        text = text.replace('"', '').replace('•', '-')
        return text

    def semantic_search_examples(self, keyword, top_k=3):
        """用 SentenceTransformer 对关键词编码，查找最相近的帖子"""
        query_vec = self.embed_model.encode([keyword])
        D, I = self.index.search(np.array(query_vec), top_k)

        examples = []
        for idx in I[0]:
            if idx < len(self.texts):
                split_text = self.texts[idx].split('。\n', 1)
                title = split_text[0] if split_text else ""
                content = split_text[1] if len(split_text) > 1 else ""
                examples.append({
                    "title": title,
                    "content": content
                })
        return examples

    def generate_post_with_examples(self, keyword):
        examples = self.semantic_search_examples(keyword)

        # 构造 prompt
        prompt = f"请根据以下示例生成一个关于“{keyword}”的论坛帖子：\n\n"
        for ex in examples:
            prompt += f"示例标题: {ex.get('title', '')}\n"
            prompt += f"示例内容: {self.clean_content(ex.get('content', ''))}\n\n"
        prompt += (
            "请根据以上风格，写一个新的中文论坛帖（像真人一样），"
            "适合留学生和找工作的用户。标题用“# 标题”格式，不要提到加米或一亩三分地。"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个中文论坛发帖助手，请模仿真实用户的语气与风格。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成失败: {e}"

# ✅ 单独调用方法（适合 CLI 或主程序入口调用）
def generate_post(keyword):
    generator = PostGenerator()
    return generator.generate_post_with_examples(keyword)
