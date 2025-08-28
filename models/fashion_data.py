from tortoise import fields
from tortoise.models import Model

class FashionData(Model):
    fashion_id = fields.IntField(pk=True, description="时装id")
    fashion_key = fields.CharField(max_length=100, unique=True, description="时装key")
    fashion_name = fields.CharField(max_length=100, description="时装名称")
    description = fields.TextField(null=True, description="时装描述")
    active_source = fields.CharField(max_length=255, null=True, description="时装来源")
    icons = fields.JSONField(null=True, description="时装图标")

    class Meta:
        table = "fashion_data"
        table_description = "时装基本信息"

    def __str__(self):
        return self.fashion_name
