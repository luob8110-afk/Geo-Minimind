import json
import random

# ==========================================
# 1. 配置文件路径与混合比例
# ==========================================
# 你刚才跑完的专属测绘数据
GIS_DATA_FILE = "sft_gis_data.jsonl"
# 刚刚下载的 5 万条通用数据
GENERAL_DATA_FILE = "alpaca_data_zh_51k.json"
# 🌟 最终拿去云端训练的“终极黄金数据集”
OUTPUT_FINAL_FILE = "final_sft_dataset.jsonl"

# 通用数据我们不需要全要，抽取 20,000 条作为“底色”即可
SAMPLE_SIZE = 20000


def main():
    print("🚀 开始构建 Geo-MiniMind 终极混合指令集...")

    # ----------------------------------------
    # 步骤 A：读取你的测绘核心数据
    # ----------------------------------------
    gis_data = []
    with open(GIS_DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                gis_data.append(json.loads(line.strip()))
    print(f"  ✅ 成功加载专属测绘 QA：{len(gis_data)} 条")

    # ----------------------------------------
    # 步骤 B：读取并清洗通用开源数据
    # ----------------------------------------
    with open(GENERAL_DATA_FILE, 'r', encoding='utf-8') as f:
        general_raw = json.load(f)

    general_data = []
    for item in general_raw:
        instruction = item.get("instruction", "")
        input_text = item.get("input", "")
        output = item.get("output", "")

        # 核心清洗：把通用数据里的 input 和 instruction 拼在一起，对齐我们的格式
        if input_text:
            instruction = f"{instruction}\n{input_text}"

        general_data.append({
            "instruction": instruction,
            "output": output
        })

    # 随机抽取 2 万条通用数据
    general_sampled = random.sample(general_data, min(SAMPLE_SIZE, len(general_data)))
    print(f"  ✅ 成功抽取通用对话 QA：{len(general_sampled)} 条")

    # ----------------------------------------
    # 步骤 C：大锅炖与洗牌 (Shuffle) - 极其关键！
    # ----------------------------------------
    final_data = gis_data + general_sampled

    # 🌟 必须打乱！如果不打乱，模型会先学完测绘再学通用，导致灾难性遗忘
    random.shuffle(final_data)

    # ----------------------------------------
    # 步骤 D：输出最终的 JSONL 文件
    # ----------------------------------------
    with open(OUTPUT_FINAL_FILE, 'w', encoding='utf-8') as f:
        for item in final_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print("\n" + "=" * 50)
    print(f"🎉 终极数据集构建完成！")
    print(f"🧠 总计数据量：{len(final_data)} 条")
    print(f"📁 请带上这个文件去云端炼丹：{OUTPUT_FINAL_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()