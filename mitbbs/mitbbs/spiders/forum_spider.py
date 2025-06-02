import scrapy
import re
from mitbbs.items import ForumPostItem

BASE_URL = "https://www.1point3acres.com/bbs/"
FORUM_ID = 28  # 要爬的版块
START_PAGE = 1
END_PAGE = 5   # 想爬多少页自己改

AD_PATTERNS = [
    r'^注册一亩三分地论坛.*?注册账号x',
    r'^This post was last edited.*?on \d{4}-\d{1,2}-\d{1,2}',
    r'^您需要登录才可以下载或查看附件。没有帐号？注册账号x',
]

def clean_text(text):
    for pattern in AD_PATTERNS:
        text = re.sub(pattern, '', text)
    return text.strip()

class ForumSpiderSpider(scrapy.Spider):
    name = "forum"
    allowed_domains = ["1point3acres.com"]
    start_urls = [
        f"{BASE_URL}forum-{FORUM_ID}-{i}.html"
        for i in range(START_PAGE, END_PAGE + 1)
    ]

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0",
            "Referer": f"{BASE_URL}forum-{FORUM_ID}-1.html"
        }
    }

    def parse(self, response):
        for tbody in response.css("tbody[id^='normalthread_']"):
            a_tag = tbody.css("th a.s.xst")
            if a_tag:
                title = a_tag.css("::text").get()
                href = a_tag.css("::attr(href)").get()
                full_link = response.urljoin(href)
                yield scrapy.Request(
                    full_link,
                    callback=self.parse_thread,
                    meta={'title': title, 'link': full_link}
                )

    def parse_thread(self, response):
        content_raw = response.css('td.t_f[id^="postmessage_"]').xpath('string(.)').get()
        content = clean_text(content_raw) if content_raw else ""

        item = ForumPostItem(
            title=response.meta['title'],
            link=response.meta['link'],
            content=content
        )
        yield item

