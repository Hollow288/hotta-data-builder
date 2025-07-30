from tortoise import fields
from tortoise.models import Model


class Weapons(Model):
    weapons_id = fields.IntField(pk=True, description="武器id")
    item_key = fields.CharField(max_length=200, description="武器key")
    item_name = fields.CharField(max_length=200, null=True, description="武器名称")
    item_rarity = fields.CharField(max_length=200, null=True, description="武器稀有度")
    weapon_category = fields.CharField(max_length=100, null=True, description="武器定位")
    weapon_element_type = fields.CharField(max_length=100, null=True, description="武器属性")
    weapon_element_name = fields.CharField(max_length=100, null=True, description="特质名称")
    weapon_element_desc = fields.CharField(max_length=1000, null=True, description="特质描述")
    armor_broken = fields.DecimalField(max_digits=18, decimal_places=4, null=True, description="武器破防")
    charging = fields.DecimalField(max_digits=18, decimal_places=4, null=True, description="武器充能")
    item_icon = fields.CharField(max_length=200, null=True, description="武器缩略图地址")
    description = fields.CharField(max_length=500, null=True, description="武器描述")
    remould_detail = fields.CharField(max_length=1000, null=True, description="专属效果")

    class Meta:
        table = "weapons"
        table_description = "武器基本信息"
