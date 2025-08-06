from tortoise import fields
from tortoise.models import Model

class RecipesIngredients(Model):
    """
    食谱食材对照
    """
    recipes_ingredients_id = fields.IntField(pk=True, description="对照id")
    ingredient_id = fields.IntField(null=True, description="食材id")
    recipes_id = fields.IntField(null=True, description="食谱id")
    amount = fields.IntField(null=True, description="数量")

    class Meta:
        table = "recipes_ingredients"
        table_description = "食谱食材对照"
