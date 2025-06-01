import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin

class ForumScraper:
    def __init__(self):
        self.base_url = "https://www.chineseinla.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay = 2  # 请求间隔秒数

    def scrape_topic_list(self, forum_url):
        """爬取论坛页面获取所有帖子标题和链接"""
        try:
            response = requests.get(forum_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            topics = []
            topic_containers = soup.find_all('div', class_='topic_list_12')
            
            for container in topic_containers:
                title_link = container.find('a', class_='title')
                if title_link:
                    title = title_link.text.strip()
                    relative_link = title_link['href']
                    full_link = urljoin(self.base_url, relative_link)
                    topics.append({'title': title, 'url': full_link})
            
            return topics
        
        except Exception as e:
            print(f"爬取帖子列表出错: {e}")
            return []

    def scrape_topic_detail(self, url):
        """爬取单个帖子的详细内容"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = soup.find('h1').text.strip() if soup.find('h1') else "无标题"
            
            # 提取详细内容
            content_div = soup.find('div', class_='rent_apartsep', string='详细描述')
            content = ""
            
            if content_div:
                real_content = content_div.find_next('p', class_='real-content')
                if real_content:
                    # 处理内容中的特殊格式
                    content_parts = []
                    for element in real_content.children:
                        if element.name == 'br':
                            continue
                        text = element.get_text(strip=True)
                        if text:
                            content_parts.append(text)
                    content = '\n'.join(content_parts)
            
            return {
                'title': title,
                'url': url,
                'content': content,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"爬取帖子详情出错 {url}: {e}")
            return None

    def scrape_forum(self, forum_url, max_posts=20):
        """完整爬取流程"""
        print("开始爬取论坛帖子列表...")
        topics = self.scrape_topic_list(forum_url)
        
        if not topics:
            print("未找到任何帖子")
            return []
        
        print(f"共找到 {len(topics)} 个帖子，开始爬取详情...")
        
        posts_data = []
        for i, topic in enumerate(topics[:max_posts], 1):
            print(f"正在处理 {i}/{len(topics[:max_posts])}: {topic['title']}")
            post_detail = self.scrape_topic_detail(topic['url'])
            if post_detail:
                posts_data.append(post_detail)
            time.sleep(self.delay)
        
        return posts_data

    def save_to_json(self, data, filename):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")

# 使用示例
if __name__ == "__main__":
    scraper = ForumScraper()
    forum_url = "https://www.chineseinla.com/f/page_viewforum/f_29.html"
    
    # 爬取数据
    posts_data = scraper.scrape_forum(forum_url, max_posts=10)  # 测试时限制为10个帖子
    
    # 保存数据
    scraper.save_to_json(posts_data, 'forum_posts.json')
    
    print("\n爬取完成！以下是部分示例数据:")
    for i, post in enumerate(posts_data[:3], 1):  # 只显示前3个作为示例
        print(f"\n示例 {i}:")
        print(f"标题: {post['title']}")
        print(f"内容: {post['content'][:200]}...")  # 只显示前200字符