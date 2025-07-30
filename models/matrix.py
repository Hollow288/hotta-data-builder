from tortoise import fields
from tortoise.models import Model

class Matrix(Model):
    matrix_id: int = fields.IntField(pk=True, description="意志id")
    matrix_key: str | None = fields.CharField(max_length=200, null=True, description="意志key")
    matrix_suit_quality: str | None = fields.CharField(max_length=200, null=True, description="意志品质")
    suit_name: str | None = fields.CharField(max_length=200, null=True, description="意志名称")
    suit_icon: str | None = fields.CharField(max_length=200, null=True, description="意志稀有度")

    class Meta:
        table = "matrix"
        table_description = "意志基本信息"
        table_kwargs = {"row_format": "dynamic"}
