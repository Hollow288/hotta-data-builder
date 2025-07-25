import json
import os

from utils import load_keys_to_entries_grouped
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

# 从 .env 获取源数据根目录
source_path = os.getenv("SOURCE_PATH")  # 例：C:/XM/MY/Hotta/Content/Resources

# 拼接成完整路径列表
paths = [
    os.path.join(source_path, "CoreBlueprints/DataTable/Skill"),
    os.path.join(source_path, "Text/ST_item.json"),
    os.path.join(source_path, "Text/ST_Equipment.json"),
    os.path.join(source_path, "Text/QRSLCommon_ST.json")
]

# 加载数据
grouped_data = load_keys_to_entries_grouped(paths)

# 构建输出路径（保存到项目根目录的 dist/intermediate/Game.json）
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist", "intermediate", "Game.json"))
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(grouped_data, f, ensure_ascii=False, indent=2)


