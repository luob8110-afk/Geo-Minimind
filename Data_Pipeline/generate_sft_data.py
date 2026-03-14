import os
import json
import time
from openai import OpenAI  # 因为 Qwen 兼容 OpenAI 接口，我们直接用官方轻量库

# ==========================================
# 1. 配置区域
# ==========================================
QWEN_API_KEY = "密钥"
INPUT_CORPUS = "csdn_gis_corpus.txt"  # 刚才爬的质量一般的纯文本
OUTPUT_SFT = "sft_gis_data.jsonl"  # 输出的高质量微调数据

# 初始化大模型客户端
client = OpenAI(
    api_key=QWEN_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


# ==========================================
# 2. 核心大模型生成逻辑 (Prompt Engineering)
# ==========================================
def generate_qa_pairs(text_chunk):
    """
    让大模型阅读一段文本，强行提取出 3 个高质量的专业问答对
    """
    prompt = f"""你是一个顶级的 GIS 与测绘学教授。
    请阅读以下提供的【参考文本】（该文本可能是从网页抓取的，可能排版混乱或包含废话）。
    你的任务是：忽略其中的废话和格式错误，提取出最核心的测绘/GIS专业知识，并生成 3 个高质量的、具有启发性的专业问答对。

    要求：
    1. 问题(instruction)必须专业、具体，不要问太宽泛的问题。
    2. 答案(output)必须条理清晰、严谨，剔除参考文本里的口语化表达。
    3. 必须严格按照下面的 JSON 数组格式输出，不要输出任何其他的解释性文字！

    期望的输出格式示例：
    [
        {{"instruction": "WGS84坐标系与CGCS2000坐标系的主要区别是什么？", "output": "WGS84和CGCS2000的主要区别在于..."}},
        {{"instruction": "...", "output": "..."}}
    ]

    【参考文本】：
    {text_chunk}
    """

    try:
        response = client.chat.completions.create(
            model="qwen-turbo",  # 使用免费额度高的模型
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # 稍微降低温度，保证回答的专业严谨性
        )
        # 获取大模型的输出
        result = response.choices[0].message.content.strip()

        # 尝试将输出的文本解析为 Python 的列表
        # 大模型有时候会在 JSON 外面包一层 ```json ... ```，需要做个简单的清理
        if result.startswith("```json"):
            result = result[7:-3].strip()
        elif result.startswith("```"):
            result = result[3:-3].strip()

        qa_list = json.loads(result)
        return qa_list
    except Exception as e:
        print(f"⚠️ 生成失败或格式解析错误: {e}")
        return []


# ==========================================
# 3. 调度管线：切块 -> 生成 -> 保存
# ==========================================
if __name__ == "__main__":
    print("🚀 开始利用 Qwen 大模型提炼高质量 SFT 问答对...")

    if not os.path.exists(INPUT_CORPUS):
        print(f"找不到语料库 {INPUT_CORPUS}，请先运行爬虫！")
        exit()

    # 读取全部文本
    with open(INPUT_CORPUS, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # 将长文本切块 (大模型一次读不完几十万字，我们每次喂给它 800 字)
    chunk_size = 800
    text_chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

    print(f"📄 语料已切分为 {len(text_chunks)} 块，准备送入大模型流水线...")

    total_qa_pairs = 0

    # 采用追加模式写入 JSONL (每行一个完整的 JSON 对象，这是大模型微调的标准格式)
    with open(OUTPUT_SFT, 'a', encoding='utf-8') as outfile:
        # 为了演示，我们先只处理前 10 块文本 (测试没问题了你再把 [:10] 删掉跑全量)
        for i, chunk in enumerate(text_chunks[4000:], start=4000):
            print(f"[{i}/共 {len(text_chunks)} 块] 正在让大模型提炼知识点...")

            qa_list = generate_qa_pairs(chunk)

            for qa in qa_list:
                # 将 Python 字典转化为 JSON 字符串并写入文件
                json_str = json.dumps(qa, ensure_ascii=False)
                outfile.write(json_str + "\n")
                total_qa_pairs += 1

            print(f"  ✅ 成功提取 {len(qa_list)} 对 QA。")

            # API 调用频率限制，防止被封
            time.sleep(1)

    print("\n" + "=" * 40)
    print(f"🎉 SFT 数据合成完毕！")
    print(f"🧠 本次共从‘质量一般’的文本中，成功提炼出 {total_qa_pairs} 条高质量的专业问答对！")
    print(f"📁 微调数据已保存至: {OUTPUT_SFT}")
    print("=" * 40)
