from tortoise import fields
from tortoise.models import Model


class ArtifactData(Model):
    """
    源器信息
    """
    artifact_id = fields.IntField(pk=True, description="源器id")
    artifact_key = fields.CharField(max_length=100, unique=True, description="源器key")
    item_rarity = fields.CharField(max_length=100, description="源器品质")
    item_name = fields.CharField(max_length=100, description="源器名称")
    card_image = fields.CharField(max_length=200, description="源器图标")
    use_description = fields.TextField(null=True, description="源器描述")
    artifact_attribute_data = fields.JSONField(null=True, description="源器星级")

    class Meta:
        table = "artifact_data"
        table_description = "源器信息"
