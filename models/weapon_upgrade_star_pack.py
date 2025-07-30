from tortoise import fields
from tortoise.models import Model


class WeaponUpgradeStarPack(Model):
    upgrade_star_id = fields.IntField(pk=True, description="星级id")
    weapons_id = fields.IntField(description="武器id")
    item_name = fields.CharField(max_length=200, null=True, description="词条名称")
    item_describe = fields.CharField(max_length=5000, null=True, description="词条描述")

    class Meta:
        table = "weapon_upgrade_star_pack"
        table_description = "武器星级"
