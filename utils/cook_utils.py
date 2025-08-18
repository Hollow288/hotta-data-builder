import re
from pathlib import Path

from utils.common_utils import extract_tail_name, format_description



def fix_food_icon_url(food_icon: str) -> str | None:
    path = Path(food_icon.strip())

    # 1. 判断原始路径是否存在
    if path.exists():
        return str(path)

    # 2. 文件不存在，尝试修改文件名
    file_name = path.name  # 取出文件名部分
    parts = file_name.split('_', 1)  # 仅分割一次，去掉第一段
    if len(parts) < 2:
        return None  # 无法重构路径

    new_file_name = parts[1]
    new_path = path.with_name(new_file_name)

    # 3. 判断新路径是否存在
    if new_path.exists():
        return str(new_path)


    # 我们在这里新增逻辑
    original_stem = path.stem  # 不带扩展名的文件名
    suffix = path.suffix

    # 匹配形如 "Item_Fishes006"
    match = re.fullmatch(r"([A-Za-z]+_)?([A-Za-z]+)(\d+)", original_stem)
    if match:
        prefix = match.group(1) or ""  # 可能为空，例如没有 Item_
        letters = match.group(2)
        digits = match.group(3)

        # Step 2: 加上下划线后再尝试
        new_stem = f"{prefix}{letters}_{digits}"
        path2 = path.with_name(new_stem + suffix)
        if path2.exists():
            return str(path2)

        # Step 3: 缩短字母部分再试（在 step 2 的基础上）
        if len(letters) > 1:
            shorter_letters = letters[:-1]
            shorter_stem = f"{prefix}{shorter_letters}_{digits}"
            path3 = path.with_name(shorter_stem + suffix)
            if path3.exists():
                return str(path3)

    # Step 4: 新增的独立尝试方式 — 第二个 "_" 前插入 "s"
    # 例如：Item_Shell_002 → Item_Shells_002
    new_stem = original_stem
    underscore_positions = [m.start() for m in re.finditer("_", new_stem)]
    if len(underscore_positions) >= 2:
        second_underscore_index = underscore_positions[1]
        # 插入一个 "s" 到第二个下划线前
        stem_modified = new_stem[:second_underscore_index] + "s" + new_stem[second_underscore_index:]
        path4 = path.with_name(stem_modified + suffix)
        if path4.exists():
            return str(path4)

    # Step5 : 手动处理
    true_map = {
        "Item_Shell_002.png" : "item_shells_002.png",
        "Item_Fruits009.png" : "Item_Fruit_007.png",
        "Item_Shell_001.png" : "item_shells_001.png",
        "Item_Condiment_07.png" : "Item_Milk_001.png",
        "Item_Fruit_001.png" : "Item_Orange.png",
        "Item_Vera_Harvest_009.png" : "Item_Pumpkin.png",
        "Item_Condiment_05.png" : "Item_Greens_005.png",
    }


    filename = path.name
    if filename in true_map:
        fixed_path = path.with_name(true_map[filename])
        if fixed_path.exists():
            return str(fixed_path)

    # 4. 都找不到
    return None


def make_recipes_name_des(food_item_id: str, cooking_food_data_table_rows_data: dict, game_json: dict) -> dict:
    food_item_info = cooking_food_data_table_rows_data[food_item_id]

    if extract_tail_name(food_item_info['Description']['TableId']) == 'UI':
        print(food_item_info['Description']['TableId'])

    return {
        "recipes_name": game_json[extract_tail_name(food_item_info['ItemName']['TableId'])][food_item_info['ItemName']['Key']],
        "recipes_des": game_json[extract_tail_name(food_item_info['Description']['TableId'])][food_item_info['Description']['Key']]
    }


def make_categories(categories: list, cooking_food_category_data_table_rows_data: dict, game_json :dict) -> str:
    result = []
    for type in categories:
        this_type = game_json[extract_tail_name(cooking_food_category_data_table_rows_data[type]['Name']['TableId'])][cooking_food_category_data_table_rows_data[type]['Name']['Key']]
        result.append(this_type)

    return " / ".join(result)


def make_use_description(tool_static_data_table_rows_data: dict, static_tool_name: str, template: str) -> str:

    value = [float(tool_static_data_table_rows_data[static_tool_name]['ToolValue'])]

    return format_description(template,value)


def make_buff(buffs: list, gameplay_effect_tips_rows_data: dict, game_json: dict) -> str:

    buff_template={
        "buff_AddPhyAtkFoodBase" : "增加物理攻击<ComLblGreen>{1}%</>，物理攻击<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddEnergyRecoverFoodBase" : "提升耐力恢复速度<ComLblGreen>{1}%</>，持续<ComLblGreen>{0}</>秒。",
        "buff_Food_JiantingDiveSpeed" : "潜泳状态下的移动速度提高<ComLblGreen>{1}%</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddThunderDefFoodBase" : "增加雷电抗性<ComLblGreen>{1}%</>，雷电抗性<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddPhyDefFoodBase" : "增加物理抗性<ComLblGreen>{1}%</>，物理抗性<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddIceAtkFoodBase" : "增加寒冰攻击<ComLblGreen>{1}%</>，寒冰攻击<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddIceDefFoodBase" : "增加寒冰抗性<ComLblGreen>{1}%</>，寒冰抗性<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddThunderAtkFoodBase" : "增加雷电攻击<ComLblGreen>{1}%，雷电攻击<ComLblGreen>{2}</>，持续{0}</>秒。",
        "buff_Food_AddRecoveryHp" : "使用后立刻恢复(<ComLblGreen>{1}%+{2}</>)生命值，随后每<ComLblGreen>{3}</>秒恢复(<ComLblGreen>{1}%+{2}</>)生命值，持续<ComLblGreen>{0}</>秒。",
        "buff_AddFireAtkFoodBase" : "增加火焰攻击<ComLblGreen>{1}%</>，火焰攻击<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_Food_CleanBuff" : "使用后解除中毒。",
        "buff_AddHealthFoodBase" : "使用后立刻恢复(<ComLblGreen>{1}%+{2}</>)点拓荒者生命值。",
        "buff_ThunderAtkFixAddFoodBase" : "使用后雷电攻击增加<ComLblGreen>{1}%，雷电抗性增加<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_AddFireDefFoodBase" : "增加火焰抗性<ComLblGreen>{1}%</>，火焰抗性<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_Food_JiantingEnergyConsumeDown" : "处于潜泳状态时，所有耐力消耗降低<ComLblGreen>33%</>，持续<ComLblGreen>{0}</>秒。",
        "buff_IceAtkFixAddFoodBase" : "使用后寒冰攻击增加<ComLblGreen>{1}%，寒冰抗性增加<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。",
        "buff_FireAtkFixAddFoodBase" : "使用后火焰攻击增加<ComLblGreen>{1}%，火焰抗性增加<ComLblGreen>{2}</>，持续<ComLblGreen>{0}</>秒。"
    }

    visible_buffs = [buff for buff in buffs if not buff.get('bNotShowInTips', False)]

    result = []

    for buff in visible_buffs:

        value = []

        value.append(buff['ModifyData']['fDuration'])
        value.append(buff['ModifyData']['fStrengthMult']*100)
        value.append(buff['ModifyData']['fStrengthAdd'])
        value.append(buff['ModifyData']['fPeriod'])

        buff_class_path = buff.get('BuffClass', {}).get('AssetPathName')

        if buff_class_path is None or buff_template.get(extract_tail_name(buff_class_path)) is None:
            row_data = gameplay_effect_tips_rows_data[extract_tail_name(buff['BuffClass']['AssetPathName'])]
            template = game_json[extract_tail_name(row_data['Desc']['TableId'])][row_data['Desc']['Key']]
        else:
            template = buff_template[extract_tail_name(buff['BuffClass']['AssetPathName'])]

        this_des = format_description(template,value)

        result.append(this_des)

    return " / ".join(result)

def make_ingredients(ingredients:list)->dict:
    result = {}
    for ingredient in ingredients:

        result[ingredient['DesignedItemsID'][0]] = ingredient['MinNeedIngredientAmount']

    return result


def make_food_source(dt_item_output_source_rows_data: dict, food_key: str, game_json: dict) -> str:

    if food_key == "Item_Dandelion_zhongzi":
        food_key = "Item_Dandelion_001"

    key = food_key.split("_", 1)[1]
    this_source = dt_item_output_source_rows_data.get(key, {"SourceArray":[]})

    result_list = []

    for item in this_source['SourceArray']:
        result_list.append(game_json[extract_tail_name(item['PostfixName']['TableId'])][item['PostfixName']['Key']])

    return " / ".join(result_list)