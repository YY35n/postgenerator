import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class FaissPipeline:
    def __init__(self):
        self.index_file = "forum_posts_index.faiss"
        self.text_file = "forum_posts_texts.json"
        self.link_file = "forum_posts_links.json"  # ✅ 新增：链接去重用
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.new_texts = []
        self.new_links = []

        # 加载旧链接和文本
        if os.path.exists(self.link_file):
            with open(self.link_file, "r", encoding='utf-8') as f:
                self.existing_links = set(json.load(f))
        else:
            self.existing_links = set()

        if os.path.exists(self.index_file) and os.path.exists(self.text_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.text_file, "r", encoding='utf-8') as f:
                self.all_texts = json.load(f)
        else:
            self.index = None
            self.all_texts = []

    def process_item(self, item, spider):
        link = item['link']
        if link in self.existing_links:
            spider.logger.info(f"⛔ 跳过重复帖子: {link}")
            return item  # 不处理重复

        text = f"{item['title']}。\n{item['content']}"
        self.new_texts.append(text)
        self.new_links.append(link)
        return item

    def close_spider(self, spider):
        if not self.new_texts:
            print("⚠️ 没有新帖子要处理")
            return

        print(f"\n🔍 正在嵌入 {len(self.new_texts)} 条新文本...")
        embeddings = self.embed_model.encode(self.new_texts, show_progress_bar=True)
        embeddings = np.array(embeddings)

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        self.all_texts.extend(self.new_texts)
        self.existing_links.update(self.new_links)

        # 保存
        faiss.write_index(self.index, self.index_file)
        with open(self.text_file, "w", encoding="utf-8") as f:
            json.dump(self.all_texts, f, ensure_ascii=False, indent=2)
        with open(self.link_file, "w", encoding="utf-8") as f:
            json.dump(list(self.existing_links), f, ensure_ascii=False, indent=2)

        print(f"\n✅ 向量库更新完成：共 {len(self.all_texts)} 条文本，{len(self.existing_links)} 个唯一链接")
