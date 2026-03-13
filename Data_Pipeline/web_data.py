import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin  # 用于拼接相对路径和绝对路径


# ==========================================
# 1. 第一阶段：自动发现链接 (侦察兵)
# ==========================================
def get_all_article_links(index_url, link_selector="a"):
    """
    访问目录页，自动提取所有文章的真实链接
    """
    print(f"🔍 [侦察阶段] 正在分析目录页: {index_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(index_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取所有的 <a> 标签
        # 进阶提示：如果网站有很多无关链接，你可以修改 link_selector，比如 ".article-list a"
        links = soup.select(link_selector)

        valid_urls = []
        for link in links:
            href = link.get('href')
            if not href:
                continue

            # 过滤掉非网页链接（比如跳转页内的锚点、javascript脚本、邮箱等）
            if href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('#'):
                continue

            # 核心技巧：很多网站写的是相对路径（比如 /article/123.html），我们需要把它拼成完整的绝对路径
            full_url = urljoin(index_url, href)

            # 去重：防止同一个链接被抓取多次
            if full_url not in valid_urls:
                valid_urls.append(full_url)

        print(f"🎯 [侦察完毕] 共发现 {len(valid_urls)} 个有效文章链接！\n")
        return valid_urls

    except Exception as e:
        print(f"❌ 目录页解析失败: {e}")
        return []


# ==========================================
# 2. 第二阶段：核心文本清洗 (收割机 - 复用之前的强力逻辑)
# ==========================================
def scrape_gis_article(url):
    """抓取网页并剥离 HTML 标签，返回纯文本"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # 杀掉无用标签
        for junk in soup(["script", "style", "nav", "footer", "header", "aside"]):
            junk.extract()

        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.splitlines()]
        valid_lines = [line for line in lines if len(line) > 5]

        return "\n".join(valid_lines)
    except Exception as e:
        print(f"  ⚠️ 抓取跳过 ({url}): {e}")
        return None

# ==========================================
# 3. 自动化调度引擎 (CSDN 定制版)
# ==========================================
if __name__ == "__main__":
    # 1. 填入你找的极品目录页 (我把网址后面那一大串追踪用的乱码去掉了，这样更干净)
    INDEX_URL = "https://blog.csdn.net/weixin_34015336/article/details/93337573"
    OUTPUT_FILE = "csdn_gis_corpus.txt"

    # 2. 🎯 精准瞄准镜：只抓取正文区域 (id="content_views") 里面的超链接 (a 标签)
    # 这样就能完美避开 CSDN 的侧边栏广告和无关推荐！
    target_urls = get_all_article_links(INDEX_URL, link_selector="#content_views a")

    if not target_urls:
        print("没有找到任何链接，程序退出。")
        exit()

    print(f"🚀 [收割阶段] 开始全自动批量提取纯文本...")
    total_chars = 0

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for i, url in enumerate(target_urls):
            print(f"[{i + 1}/{len(target_urls)}] 正在深度解析: {url}")

            article_text = scrape_gis_article(url)

            if article_text:
                f.write(article_text + "\n\n")
                char_count = len(article_text)
                total_chars += char_count
                print(f"  ✅ 成功入库: {char_count} 字符")

                # ⚠️ 针对 CSDN 的防御机制：他们反爬虫比较严，我们稍微睡久一点
            time.sleep(2.5)


    print("\n" + "=" * 50)
    print(f"🎉 自动化分布式爬取任务圆满完成！")
    print(f"💾 本次共新增纯文本: {total_chars} 个字符 (约 {total_chars / 1024 / 1024:.2f} MB)")
    print(f"📁 语料已安全追加至: {OUTPUT_FILE}")
    print("=" * 50)
