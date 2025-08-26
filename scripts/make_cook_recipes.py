import os

from dotenv import load_dotenv
import json

from utils.common_utils import find_parent_value_by_key_value, fix_resolve_resource_path, extract_tail_name
from utils.cook_utils import  make_recipes_name_des, make_categories, \
    make_use_description, make_buff, make_ingredients, make_food_source

# 加载 .env 文件
load_dotenv()

# 原数据目录
source_path = os.getenv("SOURCE_PATH")



cooking_food_data_table_path = os.getenv("COOKING_FOOD_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/cooking/CookingFoodDataTable.json"
)

# 起点文件目录
cook_recipes_data_table_path = os.getenv("COOK_RECIPES_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/cooking/CookRecipesDataTable.json"
)

# food_data_table_path = os.getenv("food_DATA_TABLE") or os.path.join(
#     source_path, "CoreBlueprints/DataTable/cooking/IngredientDataTable.json"
# )
#
dt_item_output_source_path = os.getenv("DT_ITEM_OUTPUT_SOURCE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/cooking/DT_ItemOutputSource.json"
)

# 类别
cooking_food_category_data_table_path = os.getenv("COOKING_FOOD_CATEGORY_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/cooking/CookingFoodCategoryDataTable.json"
)

tool_static_data_table_path = os.getenv("TOOL_STATIC_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/ToolStaticDataTable.json"
)

item_configs_path = os.getenv("ITEM_CONFIGS") or os.path.join(
    source_path, "CoreBlueprints/DataTable/Item/ItemConfigs.json"
)

gameplay_effect_tips_data_table_path = os.getenv("GAMEPLAY_EFFECT_TIPS_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/GameplayEffectTipsDataTable.json"
)


# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))



async def make_cook_recipes():
    with open(cooking_food_data_table_path, "r", encoding="utf-8") as f:
        cooking_food_data_table = json.load(f)

    with open(cook_recipes_data_table_path, "r", encoding="utf-8") as f:
        cook_recipes_data_table = json.load(f)

    # with open(food_data_table_path, "r", encoding="utf-8") as f:
    #     food_data_table = json.load(f)

    with open(dt_item_output_source_path, "r", encoding="utf-8") as f:
        dt_item_output_source = json.load(f)

    with open(cooking_food_category_data_table_path, "r", encoding="utf-8") as f:
        cooking_food_category_data_table = json.load(f)

    with open(tool_static_data_table_path, "r", encoding="utf-8") as f:
        tool_static_data_table = json.load(f)

    with open(item_configs_path, "r", encoding="utf-8") as f:
        item_configs_data_table = json.load(f)

    with open(gameplay_effect_tips_data_table_path, "r", encoding="utf-8") as f:
        gameplay_effect_tips_data_table = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    cooking_food_data_table_rows_data = cooking_food_data_table[0].get("Rows", {})

    cook_recipes_data_table_rows_data = cook_recipes_data_table[0].get("Rows", {})

    # food_data_table_rows_data = food_data_table[0].get("Rows", {})

    dt_item_output_source_rows_data = dt_item_output_source[0].get("Rows", {})

    cooking_food_category_data_table_rows_data = cooking_food_category_data_table[0].get("Rows", {})

    tool_static_data_table_rows_data = tool_static_data_table[0].get("Rows", {})

    item_configs_rows_data = item_configs_data_table[0].get("Rows", {})

    gameplay_effect_tips_rows_data = gameplay_effect_tips_data_table[0].get("Rows", {})


    recipes_filtered_data = {
        key: val
        for key, val in cook_recipes_data_table_rows_data.items()
        if val.get("bAddToDish") == True and val.get("ShowQuestID") == "None"
    }


    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "recipes_filtered.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recipes_filtered_data, f, ensure_ascii=False, indent=2)

    item_configs_filtered_data = {
        key: val
        for key, val in item_configs_rows_data.items()
        if val.get("ItemType") == 'ITEM_TYPE_FOOD'
           and val.get("bAutoUseWhenAdd") != True
           and val.get("ItemBrief")['Key'] != 'brief_Show'
           and val.get("FeedToCorralMonsterAddExp", 0) < 50
           and val.get("ItemIcon", {}).get("AssetPathName") != "None"
           and not (val.get("StaticToolName") == "None" and len(val.get("Buffs", [])) == 0)
    }

    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "item_configs_filtered_food.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(item_configs_filtered_data, f, ensure_ascii=False, indent=2)


    # 过滤字典，同时记录缺失项
    missing_keys = []
    filtered_data = {}
    result_food_dict = {}
    result_cook_dict = {}
    type_list = set()

    for food_key, data  in item_configs_filtered_data.items():
        food_info = {
            'food_key' : food_key,
            'food_name': game_json[extract_tail_name(data['ItemName']['TableId'])][data['ItemName']['Key']],
            'food_des': game_json[extract_tail_name(data['Description']['TableId'])][data['Description']['Key']],
            'food_icon': fix_resolve_resource_path(data['ItemIcon']['AssetPathName'], '.png'),
            'food_source': make_food_source(dt_item_output_source_rows_data,data['OutputSourceID'],game_json),
            'use_description': make_use_description(
                tool_static_data_table_rows_data,
                data['StaticToolName'],
                game_json.get(extract_tail_name(data.get('UseDescription', {}).get('TableId', '')), {}).get(data.get('UseDescription', {}).get('Key', ''), '')
            ),
            'buffs': make_buff(data['Buffs'],gameplay_effect_tips_rows_data, game_json)
        }

        result_food_dict[food_key] = food_info

    # 这里将ingredient保存方便入库
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "food.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_food_dict, f, ensure_ascii=False, indent=2)




    for recipes_key, data in recipes_filtered_data.items():

        food_info = cooking_food_data_table_rows_data[data['FoodItemID']]

        recipes_info = {
            'recipes_key' : recipes_key,
            'recipes_name' : make_recipes_name_des(data['FoodItemID'],cooking_food_data_table_rows_data,game_json)['recipes_name'],
            'recipes_des' : make_recipes_name_des(data['FoodItemID'],cooking_food_data_table_rows_data,game_json)['recipes_des'],
            'recipes_icon': fix_resolve_resource_path(food_info['ItemIcon']['AssetPathName'], '.png'),
            "categories": make_categories(food_info['Categories'], cooking_food_category_data_table_rows_data, game_json),
            'use_description' : make_use_description(tool_static_data_table_rows_data,food_info['StaticToolName'],game_json[extract_tail_name(food_info['UseDescription']['TableId'])][food_info['UseDescription']['Key']]),
            'buffs' : make_buff(food_info['Buffs'],gameplay_effect_tips_rows_data, game_json),
            'ingredients': make_ingredients(data['Ingredients'])
        }

        result_cook_dict[recipes_key] = recipes_info


    # 这里将recipes保存方便入库
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "recipes.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_cook_dict, f, ensure_ascii=False, indent=2)



