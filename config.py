import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

DISCOURSE_API_KEY_KEY = os.getenv("DISCOURSE_API_KEY_KEY")
DISCOURSE_URL = os.getenv('DISCOURSE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
CATEGORY_ID = 5
REPLY_DELAY_RANGE = (120, 180)
KEYWORD = "如何准备Uber sde1的面试"



