#!/usr/bin/env python3
"""
Weight Loss Planning System
A comprehensive system for tracking daily exercise, diet, and generating scientific weight loss plans.
"""

import json
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ActivityLevel(Enum):
    SEDENTARY = "sedentary"  # Little or no exercise
    LIGHTLY_ACTIVE = "lightly_active"  # Light exercise 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # Moderate exercise 3-5 days/week
    VERY_ACTIVE = "very_active"  # Hard exercise 6-7 days/week
    EXTRA_ACTIVE = "extra_active"  # Very hard exercise & physical job


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass
class User:
    """User profile for weight loss tracking"""
    name: str
    age: int
    gender: Gender
    height_cm: float
    current_weight_kg: float
    target_weight_kg: float
    activity_level: ActivityLevel
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    def calculate_bmr(self) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender == Gender.MALE:
            bmr = (10 * self.current_weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + 5
        else:
            bmr = (10 * self.current_weight_kg) + (6.25 * self.height_cm) - (5 * self.age) - 161
        return bmr
    
    def calculate_tdee(self) -> float:
        """Calculate Total Daily Energy Expenditure"""
        bmr = self.calculate_bmr()
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTRA_ACTIVE: 1.9
        }
        return bmr * activity_multipliers[self.activity_level]
    
    def calculate_bmi(self) -> float:
        """Calculate Body Mass Index"""
        height_m = self.height_cm / 100
        return self.current_weight_kg / (height_m ** 2)


@dataclass
class Exercise:
    """Exercise activity record"""
    name: str
    duration_minutes: int
    calories_burned: int
    date: str
    intensity: str  # low, moderate, high
    notes: str = ""
    
    @staticmethod
    def estimate_calories(activity_type: str, weight_kg: float, duration_minutes: int) -> int:
        """Estimate calories burned based on activity type and duration"""
        # METs (Metabolic Equivalent of Task) values for common activities
        met_values = {
            "walking_slow": 2.5,
            "walking_moderate": 3.5,
            "walking_fast": 4.5,
            "running_slow": 7.0,
            "running_moderate": 10.0,
            "running_fast": 12.0,
            "cycling_slow": 4.0,
            "cycling_moderate": 8.0,
            "cycling_fast": 12.0,
            "swimming": 8.0,
            "yoga": 2.5,
            "weight_training": 6.0,
            "aerobics": 7.0,
            "dancing": 4.5,
            "basketball": 8.0,
            "soccer": 10.0,
            "tennis": 7.5
        }
        
        met = met_values.get(activity_type, 4.0)  # Default to moderate activity
        calories = met * weight_kg * (duration_minutes / 60)
        return int(calories)


@dataclass
class Food:
    """Food item with nutritional information"""
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0
    serving_size: str = "1 serving"


@dataclass
class Meal:
    """Meal record containing multiple food items"""
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[Food]
    date: str
    time: str
    notes: str = ""
    
    def total_calories(self) -> int:
        """Calculate total calories in the meal"""
        return sum(food.calories for food in self.foods)
    
    def total_macros(self) -> Dict[str, float]:
        """Calculate total macronutrients"""
        return {
            "protein": sum(food.protein_g for food in self.foods),
            "carbs": sum(food.carbs_g for food in self.foods),
            "fat": sum(food.fat_g for food in self.foods),
            "fiber": sum(food.fiber_g for food in self.foods)
        }


@dataclass
class DailyRecord:
    """Daily record of exercise and diet"""
    date: str
    exercises: List[Exercise] = field(default_factory=list)
    meals: List[Meal] = field(default_factory=list)
    weight_kg: Optional[float] = None
    notes: str = ""
    
    def total_calories_consumed(self) -> int:
        """Calculate total calories consumed"""
        return sum(meal.total_calories() for meal in self.meals)
    
    def total_calories_burned(self) -> int:
        """Calculate total calories burned through exercise"""
        return sum(exercise.calories_burned for exercise in self.exercises)
    
    def net_calories(self, tdee: float) -> float:
        """Calculate net calories (consumed - TDEE - exercise)"""
        return self.total_calories_consumed() - tdee - self.total_calories_burned()


@dataclass
class WeightLossPlan:
    """Scientific weight loss plan"""
    user: User
    target_date: str
    daily_calorie_target: int
    weekly_weight_loss_kg: float
    recommended_exercises: List[Dict[str, any]]
    meal_suggestions: List[Dict[str, any]]
    
    @staticmethod
    def generate_plan(user: User, weeks: int = 12, aggressive: bool = False) -> 'WeightLossPlan':
        """Generate a scientific weight loss plan"""
        tdee = user.calculate_tdee()
        
        # Safe weight loss: 0.5-1kg per week (aggressive: up to 1.5kg)
        weekly_loss = 1.0 if aggressive else 0.75
        weight_to_lose = user.current_weight_kg - user.target_weight_kg
        
        # Adjust if target is unrealistic
        if weight_to_lose / weeks > weekly_loss:
            weeks = int(weight_to_lose / weekly_loss) + 1
        
        # Calculate daily calorie deficit (1kg fat = ~7700 calories)
        daily_deficit = (weekly_loss * 7700) / 7
        daily_calories = int(tdee - daily_deficit)
        
        # Ensure healthy minimum calories
        min_calories = 1500 if user.gender == Gender.MALE else 1200
        daily_calories = max(daily_calories, min_calories)
        
        # Generate exercise recommendations
        exercises = WeightLossPlan._generate_exercise_recommendations(user, weekly_loss)
        
        # Generate meal suggestions
        meals = WeightLossPlan._generate_meal_suggestions(daily_calories)
        
        target_date = (datetime.datetime.now() + datetime.timedelta(weeks=weeks)).isoformat()
        
        return WeightLossPlan(
            user=user,
            target_date=target_date,
            daily_calorie_target=daily_calories,
            weekly_weight_loss_kg=weekly_loss,
            recommended_exercises=exercises,
            meal_suggestions=meals
        )
    
    @staticmethod
    def _generate_exercise_recommendations(user: User, weekly_loss: float) -> List[Dict]:
        """Generate personalized exercise recommendations"""
        recommendations = []
        
        # Base recommendations on current activity level
        if user.activity_level in [ActivityLevel.SEDENTARY, ActivityLevel.LIGHTLY_ACTIVE]:
            recommendations.append({
                "type": "walking_moderate",
                "frequency": "daily",
                "duration_minutes": 30,
                "description": "Brisk walking at a moderate pace"
            })
            recommendations.append({
                "type": "weight_training",
                "frequency": "2-3 times per week",
                "duration_minutes": 30,
                "description": "Light resistance training to preserve muscle"
            })
        elif user.activity_level == ActivityLevel.MODERATELY_ACTIVE:
            recommendations.append({
                "type": "running_slow",
                "frequency": "3-4 times per week",
                "duration_minutes": 30,
                "description": "Light jogging or interval training"
            })
            recommendations.append({
                "type": "weight_training",
                "frequency": "3 times per week",
                "duration_minutes": 45,
                "description": "Moderate resistance training"
            })
        else:
            recommendations.append({
                "type": "running_moderate",
                "frequency": "4-5 times per week",
                "duration_minutes": 45,
                "description": "Moderate to intense running"
            })
            recommendations.append({
                "type": "weight_training",
                "frequency": "3-4 times per week",
                "duration_minutes": 60,
                "description": "Intense resistance training"
            })
        
        # Add variety exercises
        recommendations.append({
            "type": "yoga",
            "frequency": "1-2 times per week",
            "duration_minutes": 30,
            "description": "Flexibility and stress relief"
        })
        
        return recommendations
    
    @staticmethod
    def _generate_meal_suggestions(daily_calories: int) -> List[Dict]:
        """Generate balanced meal suggestions"""
        # Calculate macro distribution (40% carbs, 30% protein, 30% fat)
        protein_calories = daily_calories * 0.30
        carb_calories = daily_calories * 0.40
        fat_calories = daily_calories * 0.30
        
        protein_grams = protein_calories / 4
        carb_grams = carb_calories / 4
        fat_grams = fat_calories / 9
        
        suggestions = [
            {
                "meal": "breakfast",
                "calories": int(daily_calories * 0.25),
                "example": "Oatmeal with berries and Greek yogurt",
                "protein_g": protein_grams * 0.25,
                "carbs_g": carb_grams * 0.25,
                "fat_g": fat_grams * 0.25
            },
            {
                "meal": "lunch",
                "calories": int(daily_calories * 0.35),
                "example": "Grilled chicken salad with quinoa",
                "protein_g": protein_grams * 0.35,
                "carbs_g": carb_grams * 0.35,
                "fat_g": fat_grams * 0.35
            },
            {
                "meal": "dinner",
                "calories": int(daily_calories * 0.30),
                "example": "Baked fish with vegetables and brown rice",
                "protein_g": protein_grams * 0.30,
                "carbs_g": carb_grams * 0.30,
                "fat_g": fat_grams * 0.30
            },
            {
                "meal": "snacks",
                "calories": int(daily_calories * 0.10),
                "example": "Fruits, nuts, or protein shake",
                "protein_g": protein_grams * 0.10,
                "carbs_g": carb_grams * 0.10,
                "fat_g": fat_grams * 0.10
            }
        ]
        
        return suggestions


class WeightLossTracker:
    """Main system for tracking weight loss progress"""
    
    def __init__(self, data_file: str = "weight_loss_data.json"):
        self.data_file = data_file
        self.user: Optional[User] = None
        self.daily_records: List[DailyRecord] = []
        self.current_plan: Optional[WeightLossPlan] = None
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                if 'user' in data:
                    user_data = data['user']
                    user_data['gender'] = Gender(user_data['gender'])
                    user_data['activity_level'] = ActivityLevel(user_data['activity_level'])
                    self.user = User(**user_data)
                
                if 'daily_records' in data:
                    for record_data in data['daily_records']:
                        exercises = [Exercise(**e) for e in record_data.get('exercises', [])]
                        meals = []
                        for meal_data in record_data.get('meals', []):
                            foods = [Food(**f) for f in meal_data['foods']]
                            meal_data['foods'] = foods
                            meals.append(Meal(**meal_data))
                        record_data['exercises'] = exercises
                        record_data['meals'] = meals
                        self.daily_records.append(DailyRecord(**record_data))
        except FileNotFoundError:
            pass
    
    def save_data(self):
        """Save data to JSON file"""
        data = {}
        
        if self.user:
            user_dict = asdict(self.user)
            user_dict['gender'] = self.user.gender.value
            user_dict['activity_level'] = self.user.activity_level.value
            data['user'] = user_dict
        
        if self.daily_records:
            records = []
            for record in self.daily_records:
                record_dict = asdict(record)
                records.append(record_dict)
            data['daily_records'] = records
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_user(self, name: str, age: int, gender: str, height_cm: float,
                   current_weight_kg: float, target_weight_kg: float,
                   activity_level: str) -> User:
        """Create a new user profile"""
        self.user = User(
            name=name,
            age=age,
            gender=Gender(gender),
            height_cm=height_cm,
            current_weight_kg=current_weight_kg,
            target_weight_kg=target_weight_kg,
            activity_level=ActivityLevel(activity_level)
        )
        self.save_data()
        return self.user
    
    def generate_plan(self, weeks: int = 12, aggressive: bool = False) -> WeightLossPlan:
        """Generate a weight loss plan for the user"""
        if not self.user:
            raise ValueError("User profile not created")
        
        self.current_plan = WeightLossPlan.generate_plan(self.user, weeks, aggressive)
        return self.current_plan
    
    def add_exercise(self, date: str, name: str, duration_minutes: int,
                    activity_type: str = None, intensity: str = "moderate",
                    notes: str = "") -> Exercise:
        """Add an exercise record"""
        if not self.user:
            raise ValueError("User profile not created")
        
        # Estimate calories if activity type is provided
        calories = 0
        if activity_type:
            calories = Exercise.estimate_calories(
                activity_type, self.user.current_weight_kg, duration_minutes
            )
        
        exercise = Exercise(
            name=name,
            duration_minutes=duration_minutes,
            calories_burned=calories,
            date=date,
            intensity=intensity,
            notes=notes
        )
        
        # Find or create daily record
        daily_record = self._get_or_create_daily_record(date)
        daily_record.exercises.append(exercise)
        self.save_data()
        return exercise
    
    def add_meal(self, date: str, meal_type: str, foods: List[Food],
                time: str = "", notes: str = "") -> Meal:
        """Add a meal record"""
        meal = Meal(
            meal_type=meal_type,
            foods=foods,
            date=date,
            time=time or datetime.datetime.now().strftime("%H:%M"),
            notes=notes
        )
        
        daily_record = self._get_or_create_daily_record(date)
        daily_record.meals.append(meal)
        self.save_data()
        return meal
    
    def update_weight(self, date: str, weight_kg: float):
        """Update weight for a specific date"""
        daily_record = self._get_or_create_daily_record(date)
        daily_record.weight_kg = weight_kg
        
        # Update user's current weight if this is the latest entry
        if date == datetime.date.today().isoformat():
            self.user.current_weight_kg = weight_kg
        
        self.save_data()
    
    def get_progress_report(self) -> Dict:
        """Generate a progress report"""
        if not self.user or not self.daily_records:
            return {"error": "No data available"}
        
        # Calculate statistics
        total_days = len(self.daily_records)
        weights = [r.weight_kg for r in self.daily_records if r.weight_kg]
        
        if weights:
            weight_lost = weights[0] - weights[-1]
            avg_weight_loss_per_week = (weight_lost / total_days) * 7 if total_days > 0 else 0
        else:
            weight_lost = 0
            avg_weight_loss_per_week = 0
        
        # Calculate average daily calories
        total_consumed = sum(r.total_calories_consumed() for r in self.daily_records)
        total_burned = sum(r.total_calories_burned() for r in self.daily_records)
        avg_daily_consumed = total_consumed / total_days if total_days > 0 else 0
        avg_daily_burned = total_burned / total_days if total_days > 0 else 0
        
        # BMI progress
        current_bmi = self.user.calculate_bmi()
        target_bmi = self.user.target_weight_kg / ((self.user.height_cm / 100) ** 2)
        
        return {
            "user_name": self.user.name,
            "total_days_tracked": total_days,
            "current_weight_kg": self.user.current_weight_kg,
            "target_weight_kg": self.user.target_weight_kg,
            "weight_lost_kg": weight_lost,
            "avg_weekly_loss_kg": avg_weight_loss_per_week,
            "current_bmi": round(current_bmi, 2),
            "target_bmi": round(target_bmi, 2),
            "avg_daily_calories_consumed": round(avg_daily_consumed),
            "avg_daily_calories_burned": round(avg_daily_burned),
            "tdee": round(self.user.calculate_tdee()),
            "days_to_target": self._estimate_days_to_target()
        }
    
    def _get_or_create_daily_record(self, date: str) -> DailyRecord:
        """Get existing daily record or create new one"""
        for record in self.daily_records:
            if record.date == date:
                return record
        
        new_record = DailyRecord(date=date)
        self.daily_records.append(new_record)
        return new_record
    
    def _estimate_days_to_target(self) -> int:
        """Estimate days remaining to reach target weight"""
        if not self.user or len(self.daily_records) < 7:
            return -1
        
        # Calculate average weight loss rate from last 7 days
        recent_records = sorted(self.daily_records[-7:], key=lambda x: x.date)
        weights = [r.weight_kg for r in recent_records if r.weight_kg]
        
        if len(weights) < 2:
            return -1
        
        daily_loss = (weights[0] - weights[-1]) / len(weights)
        
        if daily_loss <= 0:
            return -1
        
        weight_to_lose = self.user.current_weight_kg - self.user.target_weight_kg
        return int(weight_to_lose / daily_loss)


# Example usage and testing
if __name__ == "__main__":
    # Create tracker instance
    tracker = WeightLossTracker()
    
    # Create a sample user
    user = tracker.create_user(
        name="张三",
        age=30,
        gender="male",
        height_cm=175,
        current_weight_kg=85,
        target_weight_kg=75,
        activity_level="moderately_active"
    )
    
    print(f"用户创建成功: {user.name}")
    print(f"BMI: {user.calculate_bmi():.2f}")
    print(f"BMR: {user.calculate_bmr():.0f} 卡路里/天")
    print(f"TDEE: {user.calculate_tdee():.0f} 卡路里/天")
    
    # Generate weight loss plan
    plan = tracker.generate_plan(weeks=12, aggressive=False)
    print(f"\n减肥计划:")
    print(f"目标日期: {plan.target_date}")
    print(f"每日卡路里目标: {plan.daily_calorie_target}")
    print(f"每周减重目标: {plan.weekly_weight_loss_kg}kg")
    
    # Add sample daily records
    today = datetime.date.today().isoformat()
    
    # Add exercise
    exercise = tracker.add_exercise(
        date=today,
        name="晨跑",
        duration_minutes=30,
        activity_type="running_slow",
        intensity="moderate",
        notes="感觉很好"
    )
    print(f"\n运动记录: {exercise.name} - {exercise.calories_burned} 卡路里")
    
    # Add meals
    breakfast_foods = [
        Food(name="燕麦粥", calories=150, protein_g=5, carbs_g=27, fat_g=3, fiber_g=4),
        Food(name="鸡蛋", calories=70, protein_g=6, carbs_g=1, fat_g=5),
        Food(name="苹果", calories=95, protein_g=0.5, carbs_g=25, fat_g=0.3, fiber_g=4)
    ]
    
    meal = tracker.add_meal(
        date=today,
        meal_type="breakfast",
        foods=breakfast_foods,
        notes="营养均衡的早餐"
    )
    print(f"餐食记录: {meal.meal_type} - {meal.total_calories()} 卡路里")
    
    # Update weight
    tracker.update_weight(today, 84.5)
    
    # Get progress report
    report = tracker.get_progress_report()
    print(f"\n进度报告:")
    for key, value in report.items():
        print(f"  {key}: {value}")