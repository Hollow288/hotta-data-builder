from tortoise import fields
from tortoise.models import Model


class FoodData(Model):
    """
    食物信息(非制作)
    """
    food_id = fields.IntField(pk=True, description="食材id")
    food_key = fields.CharField(max_length=200, null=True, description="食材key")
    food_name = fields.CharField(max_length=200, null=True, description="食材名称")
    food_des = fields.CharField(max_length=200, null=True, description="食材描述")
    food_icon = fields.CharField(max_length=200, null=True, description="食材缩略图地址")
    food_source = fields.CharField(max_length=200, null=True, description="食材来源")
    use_description = fields.CharField(max_length=300, null=True, description="效果描述")
    buffs = fields.CharField(max_length=300, null=True, description="buff")

    class Meta:
        table = "food_data_table"
        table_description = "食物信息(非制作)"
