from tortoise import fields
from tortoise.models import Model


class WeaponSensualityLevelData(Model):
    sensuality_id = fields.IntField(pk=True, description="通感id")
    weapons_id = fields.IntField(description="武器id")
    item_name = fields.CharField(max_length=200, null=True, description="词条名称")
    item_describe = fields.CharField(max_length=5000, null=True, description="词条描述")

    class Meta:
        table = "weapon_sensuality_level_data"
        table_description = "武器通感"
