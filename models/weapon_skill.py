from tortoise import fields
from tortoise.models import Model


class WeaponSkill(Model):
    skill_id = fields.IntField(pk=True, description="技能id")
    weapons_id = fields.IntField(description="武器id")
    skill_type = fields.CharField(max_length=200, null=True, description="类型")
    icon = fields.CharField(max_length=200, null=True, description="武器技能")
    item_name = fields.CharField(max_length=200, null=True, description="词条名称")
    item_describe = fields.CharField(max_length=5000, null=True, description="词条描述")

    class Meta:
        table = "weapon_skill"
        table_description = "武器技能"
