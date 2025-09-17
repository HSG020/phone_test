# 科学减肥计划系统

一个全面的减肥追踪系统，可以记录每日运动和饮食，并生成科学的减肥计划。

## 功能特点

### 核心功能
- **用户档案管理**: 创建和管理个人健康档案
- **科学减肥计划**: 基于个人数据生成定制化减肥计划
- **运动追踪**: 记录每日运动并自动计算卡路里消耗
- **饮食记录**: 详细记录每餐食物和营养成分
- **体重监测**: 追踪体重变化趋势
- **进度报告**: 生成详细的减肥进度分析

### 科学算法
- **BMI计算**: 身体质量指数评估
- **BMR计算**: 基础代谢率（Mifflin-St Jeor公式）
- **TDEE计算**: 每日总能量消耗
- **卡路里估算**: 基于MET值的运动卡路里消耗计算

## 使用方法

### 命令行界面使用

1. 运行程序:
```bash
python weight_loss_cli.py
```

2. 按照菜单提示操作:
   - 首次使用需要创建用户档案
   - 生成个性化减肥计划
   - 每日记录运动和饮食
   - 定期更新体重
   - 查看进度报告

### 程序化使用

```python
from weight_loss_system import WeightLossTracker

# 创建追踪器
tracker = WeightLossTracker()

# 创建用户
user = tracker.create_user(
    name="张三",
    age=30,
    gender="male",
    height_cm=175,
    current_weight_kg=85,
    target_weight_kg=75,
    activity_level="moderately_active"
)

# 生成减肥计划
plan = tracker.generate_plan(weeks=12, aggressive=False)

# 记录运动
exercise = tracker.add_exercise(
    date="2024-01-20",
    name="晨跑",
    duration_minutes=30,
    activity_type="running_slow"
)

# 记录饮食
from weight_loss_system import Food
foods = [
    Food(name="燕麦粥", calories=150, protein_g=5, carbs_g=27, fat_g=3),
    Food(name="鸡蛋", calories=70, protein_g=6, carbs_g=1, fat_g=5)
]
meal = tracker.add_meal(
    date="2024-01-20",
    meal_type="breakfast",
    foods=foods
)

# 更新体重
tracker.update_weight("2024-01-20", 84.5)

# 获取进度报告
report = tracker.get_progress_report()
```

## 系统架构

### 核心类

1. **User**: 用户档案
   - 基本信息（姓名、年龄、性别、身高、体重）
   - 活动水平
   - BMI/BMR/TDEE计算

2. **Exercise**: 运动记录
   - 运动类型、时长、强度
   - 卡路里消耗估算
   - 支持多种运动类型

3. **Food**: 食物信息
   - 营养成分（卡路里、蛋白质、碳水、脂肪、纤维）
   - 份量信息

4. **Meal**: 餐食记录
   - 餐食类型（早餐、午餐、晚餐、加餐）
   - 包含多个食物
   - 营养统计

5. **DailyRecord**: 每日记录
   - 运动列表
   - 餐食列表
   - 体重记录
   - 卡路里平衡计算

6. **WeightLossPlan**: 减肥计划
   - 个性化目标设定
   - 运动建议
   - 饮食建议
   - 时间规划

7. **WeightLossTracker**: 主追踪器
   - 数据持久化（JSON）
   - 综合管理功能
   - 进度分析

## 运动类型支持

系统支持以下运动类型的卡路里估算：
- 步行（慢速/中速/快速）
- 跑步（慢速/中速/快速）
- 骑自行车（慢速/中速/快速）
- 游泳
- 瑜伽
- 力量训练
- 有氧操
- 舞蹈
- 篮球
- 足球
- 网球

## 数据存储

数据保存在 `weight_loss_data.json` 文件中，包括：
- 用户档案
- 所有每日记录
- 运动和饮食历史

## 减肥计划算法

### 卡路里缺口计算
- 安全模式：每周减重0.5-1公斤
- 激进模式：每周减重最多1.5公斤
- 1公斤脂肪 ≈ 7700卡路里

### 最低卡路里保障
- 男性：最低1500卡路里/天
- 女性：最低1200卡路里/天

### 营养分配建议
- 碳水化合物：40%
- 蛋白质：30%
- 脂肪：30%

## 注意事项

1. **健康第一**: 本系统提供的是科学建议，实际执行请咨询医生或营养师
2. **循序渐进**: 不建议过度激进的减重目标
3. **均衡饮食**: 注意营养均衡，不要只关注卡路里
4. **规律运动**: 结合有氧运动和力量训练
5. **充足睡眠**: 保证充足的休息时间
6. **水分补充**: 每日饮水量要充足

## 系统要求

- Python 3.6+
- 无需额外依赖包（仅使用标准库）

## 文件说明

- `weight_loss_system.py`: 核心系统实现
- `weight_loss_cli.py`: 命令行界面
- `weight_loss_data.json`: 数据存储文件（自动生成）
- `requirements.txt`: 依赖说明（无外部依赖）

## 未来改进方向

- 添加图表可视化功能
- 支持多用户
- 添加食物数据库
- 集成智能推荐系统
- 移动端应用开发
- 社交分享功能
- 定时提醒功能

## 许可证

MIT License