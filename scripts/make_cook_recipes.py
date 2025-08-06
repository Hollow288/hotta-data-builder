import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
import json

from utils.common_utils import find_parent_value_by_key_value, resolve_resource_path, extract_tail_name
from utils.cook_utils import make_ingredient_icon_url, make_ingredient_name_des, make_recipes_name_des, make_categories, \
    make_use_description, make_buff, make_ingredients

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

# ingredient_data_table_path = os.getenv("INGREDIENT_DATA_TABLE") or os.path.join(
#     source_path, "CoreBlueprints/DataTable/cooking/IngredientDataTable.json"
# )
#
# dt_item_output_source_path = os.getenv("DT_ITEM_OUTPUT_SOURCE") or os.path.join(
#     source_path, "CoreBlueprints/DataTable/cooking/DT_ItemOutputSource.json"
# )

# 类别
cooking_food_category_data_table_path = os.getenv("COOKING_FOOD_CATEGORY_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/cooking/CookingFoodCategoryDataTable.json"
)

tool_static_data_table_path = os.getenv("TOOL_STATIC_DATA_TABLE") or os.path.join(
    source_path, "CoreBlueprints/DataTable/ToolStaticDataTable.json"
)


# Game.json文件目录
game_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "Game.json"))



if __name__ == "__main__":
    with open(cooking_food_data_table_path, "r", encoding="utf-8") as f:
        cooking_food_data_table = json.load(f)

    with open(cook_recipes_data_table_path, "r", encoding="utf-8") as f:
        cook_recipes_data_table = json.load(f)

    # with open(ingredient_data_table_path, "r", encoding="utf-8") as f:
    #     ingredient_data_table = json.load(f)

    # with open(dt_item_output_source_path, "r", encoding="utf-8") as f:
    #     dt_item_output_source = json.load(f)

    with open(cooking_food_category_data_table_path, "r", encoding="utf-8") as f:
        cooking_food_category_data_table = json.load(f)

    with open(tool_static_data_table_path, "r", encoding="utf-8") as f:
        tool_static_data_table = json.load(f)

    with open(game_json_path, "r", encoding="utf-8") as f:
        game_json = json.load(f)

    cooking_food_data_table_rows_data = cooking_food_data_table[0].get("Rows", {})

    cook_recipes_data_table_rows_data = cook_recipes_data_table[0].get("Rows", {})

    # ingredient_data_table_rows_data = ingredient_data_table[0].get("Rows", {})

    # dt_item_output_source_rows_data = dt_item_output_source[0].get("Rows", {})

    cooking_food_category_data_table_rows_data = cooking_food_category_data_table[0].get("Rows", {})

    tool_static_data_table_rows_data = tool_static_data_table[0].get("Rows", {})


    recipes_filtered_data = {
        key: val
        for key, val in cook_recipes_data_table_rows_data.items()
        if val.get("bAddToDish") == True and val.get("ShowQuestID") == "None"
    }


    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "dist/intermediate", "recipes_filtered.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recipes_filtered_data, f, ensure_ascii=False, indent=2)

    designed_item_ids_set = set()

    for recipe in recipes_filtered_data.values():
        for ingredient in recipe.get("Ingredients", []):
            for item_id in ingredient.get("DesignedItemsID", []):
                if item_id:  # 防止 None 或空字符串
                    designed_item_ids_set.add(item_id)

    # 过滤字典，同时记录缺失项
    missing_keys = []
    filtered_data = {}
    result_ingredient_dict = {}
    result_cook_dict = {}
    type_list = set()

    for item_id in designed_item_ids_set:
        ingredient_info = {
            'ingredient_key' : item_id,
            'ingredient_name': make_ingredient_name_des(item_id,game_json)['ingredient_name'],
            'ingredient_des': make_ingredient_name_des(item_id,game_json)['ingredient_des'],
            'ingredient_icon': make_ingredient_icon_url(source_path,item_id)
        }

        result_ingredient_dict[item_id] = ingredient_info

    # 这里将ingredient保存方便入库
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "ingredient.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_ingredient_dict, f, ensure_ascii=False, indent=2)




    for recipes_key, data in recipes_filtered_data.items():

        food_info = cooking_food_data_table_rows_data[data['FoodItemID']]

        recipes_info = {
            'recipes_key' : recipes_key,
            'recipes_name' : make_recipes_name_des(data['FoodItemID'],cooking_food_data_table_rows_data,game_json)['recipes_name'],
            'recipes_des' : make_recipes_name_des(data['FoodItemID'],cooking_food_data_table_rows_data,game_json)['recipes_des'],
            'recipes_icon': resolve_resource_path(food_info['ItemIcon']['AssetPathName'], '.png'),
            "categories": make_categories(food_info['Categories'], cooking_food_category_data_table_rows_data, game_json),
            'use_description' : make_use_description(tool_static_data_table_rows_data,food_info['StaticToolName'],game_json[extract_tail_name(food_info['UseDescription']['TableId'])][food_info['UseDescription']['Key']]),
            'buffs' : make_buff(food_info['Buffs']),
            'ingredients': make_ingredients(data['Ingredients'])
        }

        result_cook_dict[recipes_key] = recipes_info


    # 这里将ingredient保存方便入库
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist/final", "recipes.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_cook_dict, f, ensure_ascii=False, indent=2)



