from tortoise import fields
from tortoise.models import Model


class IngredientData(Model):
    ingredient_id = fields.IntField(pk=True, description="食材id")  # 对应 ingredient_id
    ingredient_key = fields.CharField(max_length=200, null=True, description="食材key")
    ingredient_name = fields.CharField(max_length=200, null=True, description="食材名称")
    ingredient_des = fields.CharField(max_length=200, null=True, description="食材描述")
    ingredient_icon = fields.CharField(max_length=200, null=True, description="食材缩略图地址")

    class Meta:
        table = "ingredient_data_table"
        table_description = "食材信息表"
