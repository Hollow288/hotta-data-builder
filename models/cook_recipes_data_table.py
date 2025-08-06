from tortoise import fields
from tortoise.models import Model

class CookRecipesDataTable(Model):
    """
    食谱数据表
    """
    recipes_id = fields.IntField(pk=True, description="食谱id")
    recipes_key = fields.CharField(max_length=200, null=True, description="食谱key")
    recipes_name = fields.CharField(max_length=200, null=True, description="食谱名称")
    recipes_des = fields.CharField(max_length=300, null=True, description="描述")
    recipes_icon = fields.CharField(max_length=200, null=True, description="图标")
    categories = fields.CharField(max_length=200, null=True, description="分类")
    use_description = fields.CharField(max_length=300, null=True, description="效果描述")
    buffs = fields.CharField(max_length=300, null=True, description="buff")

    class Meta:
        table = "cook_recipes_data_table"
        table_description = "食谱"
