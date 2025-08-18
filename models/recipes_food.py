from tortoise import fields
from tortoise.models import Model

class RecipesFood(Model):
    """
    食谱食材对照
    """
    recipes_ingredients_id = fields.IntField(pk=True, description="对照id")
    food_id = fields.IntField(null=True, description="食材id")
    recipes_id = fields.IntField(null=True, description="食谱id")
    amount = fields.IntField(null=True, description="数量")

    class Meta:
        table = "recipes_food"
        table_description = "食谱食材对照"
