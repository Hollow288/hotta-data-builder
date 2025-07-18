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

  