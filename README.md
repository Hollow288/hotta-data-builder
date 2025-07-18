### 文件结构

- ##### Weapon列表，作为组合数据的起点

  **路径**：Content/Resources/CoreBlueprints/DataTable/StaticWeaponDataTable.json

  **备注**：使用``IsWarehouseWeapon``来过滤出有用的数据

- ##### 星级效果

  **路径**：Content/Resources/CoreBlueprints/DataTable/WeaponUpgradeStarData.json

  **备注**：以Weapon列表中``UpgradeStarPackID``属性加``_X``来表示星级效果，``_0``表示基础效果，例如专属效果``xxx-驻场``；关于``RemouldDetail``描述中的占位符具体的数值，``RemouldDetailParams``为具体数值所组成的数组（按顺序），从``RemouldDetailParams``中每个元素的``ObjectPath``找到对应``json``文件，根据``RowName``找到对应的``Keys``中的``Value``，然后乘以``RemouldDetailParams``中的``Value``

- ##### 通感效果

  **路径**：Content/Resources/CoreBlueprints/DataTable/WeaponData/DT_WeaponSensualityLevelData.json

  **备注**：以Weapon列表中``SensualityPackId``属性加``_X``来表示通感效果，具体描述和对应数值取法和星级效果一致。

- ##### **技能列表（包括普通、闪避、技能、联携）**

  **路径**：Content/Resources/CoreBlueprints/DataTable/GameplayAbilityTipsDataTable.json

  **备注**：以Weapon列表中``WeaponSkillList``属性为起点，一般数组中有四个属性，分别是普通、闪避、技能、联携，然后在``GameplayAbilityTipsDataTable``中找到对应的元素，这里每个元素中的``GABranchStruct``不同方式的攻击，例如多种普通攻击方式，如果涉及到动态数值，参考**技能升级属性**

- ##### **技能升级属性**

  **路径**：Content/Resources/CoreBlueprints/DataTable/Skill/SkillUpdateTips.json

  **备注**：以``GameplayAbilityTipsDataTable``表中每个元素中``GABranchStruct``数组中每个元素的``Key``去``SkillUpdateTips``中查对应元素，具体方式为``Key``拼接``_x``,这里的x并非代表技能等级，而是技能描述中数值占位符次序，具体数值在``Key_x``元素的``Keys``数组中，这里其中数组中每个元素的``Time``为武器等级，``Value``为具体的占位符数值，一般来说武器等级都为21级，例如：没有``Time``为2的数值，那么就按``Time``为1的``Value``算。