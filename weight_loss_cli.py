#!/usr/bin/env python3
"""
Weight Loss System CLI Interface
Interactive command-line interface for the weight loss tracking system.
"""

import sys
import datetime
from weight_loss_system import (
    WeightLossTracker, User, Exercise, Food, Meal,
    ActivityLevel, Gender, WeightLossPlan
)


class WeightLossCLI:
    """Command-line interface for weight loss tracking"""
    
    def __init__(self):
        self.tracker = WeightLossTracker()
        self.commands = {
            '1': self.create_user,
            '2': self.generate_plan,
            '3': self.add_exercise,
            '4': self.add_meal,
            '5': self.update_weight,
            '6': self.view_progress,
            '7': self.view_today_summary,
            '8': self.view_plan,
            '9': self.exit_program
        }
    
    def run(self):
        """Main CLI loop"""
        print("=" * 60)
        print("欢迎使用科学减肥计划系统")
        print("=" * 60)
        
        while True:
            self.show_menu()
            choice = input("\n请选择操作 (1-9): ").strip()
            
            if choice in self.commands:
                self.commands[choice]()
            else:
                print("❌ 无效选择，请重试")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 40)
        print("主菜单")
        print("=" * 40)
        
        if self.tracker.user:
            print(f"当前用户: {self.tracker.user.name}")
            print(f"当前体重: {self.tracker.user.current_weight_kg}kg")
            print(f"目标体重: {self.tracker.user.target_weight_kg}kg")
        else:
            print("⚠️  未创建用户档案")
        
        print("\n选项:")
        print("1. 创建/更新用户档案")
        print("2. 生成减肥计划")
        print("3. 记录运动")
        print("4. 记录饮食")
        print("5. 更新体重")
        print("6. 查看进度报告")
        print("7. 查看今日总结")
        print("8. 查看减肥计划")
        print("9. 退出")
    
    def create_user(self):
        """Create or update user profile"""
        print("\n创建用户档案")
        print("-" * 40)
        
        try:
            name = input("姓名: ").strip()
            age = int(input("年龄: "))
            
            print("性别 (1=男性, 2=女性)")
            gender_choice = input("选择: ").strip()
            gender = "male" if gender_choice == "1" else "female"
            
            height_cm = float(input("身高 (厘米): "))
            current_weight = float(input("当前体重 (公斤): "))
            target_weight = float(input("目标体重 (公斤): "))
            
            print("\n活动水平:")
            print("1. 久坐 (很少或没有运动)")
            print("2. 轻度活跃 (每周轻度运动1-3天)")
            print("3. 中度活跃 (每周中度运动3-5天)")
            print("4. 非常活跃 (每周剧烈运动6-7天)")
            print("5. 极度活跃 (非常剧烈的运动和体力工作)")
            
            activity_choice = input("选择 (1-5): ").strip()
            activity_levels = {
                '1': 'sedentary',
                '2': 'lightly_active',
                '3': 'moderately_active',
                '4': 'very_active',
                '5': 'extra_active'
            }
            activity_level = activity_levels.get(activity_choice, 'moderately_active')
            
            user = self.tracker.create_user(
                name=name,
                age=age,
                gender=gender,
                height_cm=height_cm,
                current_weight_kg=current_weight,
                target_weight_kg=target_weight,
                activity_level=activity_level
            )
            
            print(f"\n✅ 用户档案创建成功!")
            print(f"BMI: {user.calculate_bmi():.2f}")
            print(f"基础代谢率: {user.calculate_bmr():.0f} 卡路里/天")
            print(f"每日总能量消耗: {user.calculate_tdee():.0f} 卡路里/天")
            
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 创建失败: {e}")
    
    def generate_plan(self):
        """Generate weight loss plan"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n生成减肥计划")
        print("-" * 40)
        
        try:
            weeks = int(input("计划周数 (建议8-16周): ") or "12")
            aggressive = input("是否采用激进模式? (y/n): ").lower() == 'y'
            
            plan = self.tracker.generate_plan(weeks, aggressive)
            
            print(f"\n✅ 减肥计划生成成功!")
            print(f"目标完成日期: {plan.target_date[:10]}")
            print(f"每日卡路里目标: {plan.daily_calorie_target} 卡")
            print(f"每周减重目标: {plan.weekly_weight_loss_kg} 公斤")
            
            print("\n推荐运动:")
            for exercise in plan.recommended_exercises:
                print(f"  • {exercise['description']}")
                print(f"    频率: {exercise['frequency']}, 时长: {exercise['duration_minutes']}分钟")
            
            print("\n饮食建议:")
            for meal in plan.meal_suggestions:
                print(f"  • {meal['meal']}: {meal['calories']} 卡路里")
                print(f"    示例: {meal['example']}")
                
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 生成失败: {e}")
    
    def add_exercise(self):
        """Add exercise record"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n记录运动")
        print("-" * 40)
        
        try:
            date = input(f"日期 (YYYY-MM-DD) [默认今天]: ").strip()
            if not date:
                date = datetime.date.today().isoformat()
            
            name = input("运动名称: ").strip()
            duration = int(input("时长 (分钟): "))
            
            print("\n运动类型 (用于估算卡路里):")
            print("1. 慢走  2. 中速走  3. 快走")
            print("4. 慢跑  5. 中速跑  6. 快跑")
            print("7. 骑车  8. 游泳  9. 瑜伽")
            print("10. 力量训练  11. 有氧操  12. 其他")
            
            type_choice = input("选择 (1-12): ").strip()
            activity_types = {
                '1': 'walking_slow', '2': 'walking_moderate', '3': 'walking_fast',
                '4': 'running_slow', '5': 'running_moderate', '6': 'running_fast',
                '7': 'cycling_moderate', '8': 'swimming', '9': 'yoga',
                '10': 'weight_training', '11': 'aerobics'
            }
            activity_type = activity_types.get(type_choice)
            
            intensity = input("强度 (低/中/高) [默认中]: ").strip() or "中"
            notes = input("备注 (可选): ").strip()
            
            exercise = self.tracker.add_exercise(
                date=date,
                name=name,
                duration_minutes=duration,
                activity_type=activity_type,
                intensity=intensity,
                notes=notes
            )
            
            print(f"\n✅ 运动记录成功!")
            print(f"消耗卡路里: {exercise.calories_burned} 卡")
            
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 记录失败: {e}")
    
    def add_meal(self):
        """Add meal record"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n记录饮食")
        print("-" * 40)
        
        try:
            date = input(f"日期 (YYYY-MM-DD) [默认今天]: ").strip()
            if not date:
                date = datetime.date.today().isoformat()
            
            print("餐食类型: 1.早餐  2.午餐  3.晚餐  4.加餐")
            meal_choice = input("选择 (1-4): ").strip()
            meal_types = {'1': '早餐', '2': '午餐', '3': '晚餐', '4': '加餐'}
            meal_type = meal_types.get(meal_choice, '加餐')
            
            foods = []
            print("\n添加食物 (输入'完成'结束):")
            
            while True:
                food_name = input("食物名称: ").strip()
                if food_name.lower() in ['完成', 'done', '']:
                    break
                
                calories = int(input("  卡路里: "))
                protein = float(input("  蛋白质(克): ") or "0")
                carbs = float(input("  碳水化合物(克): ") or "0")
                fat = float(input("  脂肪(克): ") or "0")
                fiber = float(input("  纤维(克) [可选]: ") or "0")
                serving = input("  份量 [可选]: ").strip() or "1份"
                
                food = Food(
                    name=food_name,
                    calories=calories,
                    protein_g=protein,
                    carbs_g=carbs,
                    fat_g=fat,
                    fiber_g=fiber,
                    serving_size=serving
                )
                foods.append(food)
                print(f"  ✓ 已添加 {food_name}")
            
            if foods:
                time = input("用餐时间 (HH:MM) [可选]: ").strip()
                notes = input("备注 [可选]: ").strip()
                
                meal = self.tracker.add_meal(
                    date=date,
                    meal_type=meal_type,
                    foods=foods,
                    time=time,
                    notes=notes
                )
                
                print(f"\n✅ 餐食记录成功!")
                print(f"总卡路里: {meal.total_calories()} 卡")
                macros = meal.total_macros()
                print(f"营养素: 蛋白质 {macros['protein']:.1f}g, "
                      f"碳水 {macros['carbs']:.1f}g, "
                      f"脂肪 {macros['fat']:.1f}g")
            else:
                print("❌ 未添加任何食物")
                
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 记录失败: {e}")
    
    def update_weight(self):
        """Update weight record"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n更新体重")
        print("-" * 40)
        
        try:
            date = input(f"日期 (YYYY-MM-DD) [默认今天]: ").strip()
            if not date:
                date = datetime.date.today().isoformat()
            
            weight = float(input("体重 (公斤): "))
            
            self.tracker.update_weight(date, weight)
            
            print(f"\n✅ 体重更新成功!")
            
            # Calculate progress
            weight_lost = self.tracker.user.current_weight_kg - weight
            if date == datetime.date.today().isoformat():
                if weight_lost > 0:
                    print(f"已减重: {weight_lost:.1f} 公斤")
                elif weight_lost < 0:
                    print(f"体重增加: {abs(weight_lost):.1f} 公斤")
                    
        except ValueError as e:
            print(f"❌ 输入错误: {e}")
        except Exception as e:
            print(f"❌ 更新失败: {e}")
    
    def view_progress(self):
        """View progress report"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n进度报告")
        print("=" * 40)
        
        report = self.tracker.get_progress_report()
        
        if 'error' in report:
            print(f"❌ {report['error']}")
            return
        
        print(f"用户: {report['user_name']}")
        print(f"追踪天数: {report['total_days_tracked']}")
        print(f"\n体重进度:")
        print(f"  当前体重: {report['current_weight_kg']} kg")
        print(f"  目标体重: {report['target_weight_kg']} kg")
        print(f"  已减重: {report['weight_lost_kg']:.2f} kg")
        print(f"  平均每周减重: {report['avg_weekly_loss_kg']:.2f} kg")
        
        print(f"\nBMI:")
        print(f"  当前BMI: {report['current_bmi']}")
        print(f"  目标BMI: {report['target_bmi']}")
        
        print(f"\n每日平均:")
        print(f"  摄入卡路里: {report['avg_daily_calories_consumed']} 卡")
        print(f"  消耗卡路里: {report['avg_daily_calories_burned']} 卡")
        print(f"  TDEE: {report['tdee']} 卡")
        
        if report['days_to_target'] > 0:
            print(f"\n预计达到目标需要: {report['days_to_target']} 天")
    
    def view_today_summary(self):
        """View today's summary"""
        if not self.tracker.user:
            print("❌ 请先创建用户档案")
            return
        
        print("\n今日总结")
        print("=" * 40)
        
        today = datetime.date.today().isoformat()
        today_record = None
        
        for record in self.tracker.daily_records:
            if record.date == today:
                today_record = record
                break
        
        if not today_record:
            print("今日还没有任何记录")
            return
        
        print(f"日期: {today}")
        
        if today_record.weight_kg:
            print(f"体重: {today_record.weight_kg} kg")
        
        print(f"\n运动 ({len(today_record.exercises)} 项):")
        total_exercise_calories = 0
        for exercise in today_record.exercises:
            print(f"  • {exercise.name}: {exercise.duration_minutes}分钟, "
                  f"{exercise.calories_burned}卡路里")
            total_exercise_calories += exercise.calories_burned
        print(f"  总消耗: {total_exercise_calories} 卡路里")
        
        print(f"\n饮食 ({len(today_record.meals)} 餐):")
        total_food_calories = 0
        for meal in today_record.meals:
            calories = meal.total_calories()
            print(f"  • {meal.meal_type}: {calories} 卡路里")
            total_food_calories += calories
        print(f"  总摄入: {total_food_calories} 卡路里")
        
        # Calculate net calories
        tdee = self.tracker.user.calculate_tdee()
        net = total_food_calories - tdee - total_exercise_calories
        
        print(f"\n能量平衡:")
        print(f"  TDEE: {tdee:.0f} 卡路里")
        print(f"  净卡路里: {net:.0f} 卡路里")
        
        if net < 0:
            print(f"  ✅ 卡路里缺口: {abs(net):.0f} (有助于减重)")
        else:
            print(f"  ⚠️  卡路里过剩: {net:.0f} (可能导致增重)")
    
    def view_plan(self):
        """View current weight loss plan"""
        if not self.tracker.current_plan:
            print("❌ 还未生成减肥计划")
            return
        
        plan = self.tracker.current_plan
        
        print("\n当前减肥计划")
        print("=" * 40)
        print(f"目标完成日期: {plan.target_date[:10]}")
        print(f"每日卡路里目标: {plan.daily_calorie_target} 卡")
        print(f"每周减重目标: {plan.weekly_weight_loss_kg} 公斤")
        
        print("\n推荐运动计划:")
        for i, exercise in enumerate(plan.recommended_exercises, 1):
            print(f"{i}. {exercise['description']}")
            print(f"   频率: {exercise['frequency']}")
            print(f"   时长: {exercise['duration_minutes']} 分钟")
        
        print("\n每日饮食建议:")
        total_calories = 0
        for meal in plan.meal_suggestions:
            print(f"• {meal['meal']}: {meal['calories']} 卡路里")
            print(f"  示例: {meal['example']}")
            print(f"  营养: 蛋白质 {meal['protein_g']:.0f}g, "
                  f"碳水 {meal['carbs_g']:.0f}g, "
                  f"脂肪 {meal['fat_g']:.0f}g")
            total_calories += meal['calories']
        print(f"\n总计: {total_calories} 卡路里")
    
    def exit_program(self):
        """Exit the program"""
        print("\n感谢使用减肥计划系统！")
        print("保持健康，继续努力！💪")
        sys.exit(0)


if __name__ == "__main__":
    cli = WeightLossCLI()
    cli.run()