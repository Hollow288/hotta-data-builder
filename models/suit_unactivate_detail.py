from tortoise import fields
from tortoise.models import Model

class SuitUnactivateDetail(Model):
    detail_id: int = fields.IntField(pk=True, description="意志套装id")
    matrix_id: int | None = fields.IntField(null=True, description="意志id")
    item_name: str | None = fields.CharField(max_length=200, null=True, description="套装名称")
    item_describe: str | None = fields.CharField(max_length=5000, null=True, description="套装描述")

    class Meta:
        table = "suit_unactivate_detail"
        table_description = "意志套装效果"
        table_kwargs = {"row_format": "dynamic"}
