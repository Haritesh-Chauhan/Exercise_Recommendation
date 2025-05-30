import random
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FitnessLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class HealthCondition(str, Enum):
    KNEE_PAIN = "Knee Pain"
    BACK_PAIN = "Back Pain"
    HEART_CONDITION = "Heart Condition"
    SHOULDER_INJURY = "Shoulder Injury"


@dataclass
class UserProfile:
    age: int
    height: float
    weight: float
    gender: str
    fitness_level: FitnessLevel
    health_conditions: List[HealthCondition]
    goal: str
    preferred_days: int


class ExerciseDatabase:
    def __init__(self):
        self.workout_types = {
            'Cardio': [
                'Treadmill', 'Cycling', 'Swimming', 'Rowing', 'Elliptical',
                'Jump Rope', 'Running', 'Stair Climbing', 'Boxing', 'Kickboxing',
                'Dancing', 'Mountain Climbers', 'Burpees', 'High Knees'
            ],
            'Strength': [
                'Squats', 'Deadlifts', 'Bench Press', 'Shoulder Press',
                'Pull-ups', 'Push-ups', 'Lunges', 'Dumbbell Rows',
                'Leg Press', 'Tricep Dips', 'Bicep Curls', 'Plank Holds',
                'Romanian Deadlifts', 'Hip Thrusts', 'Face Pulls'
            ],
            'Flexibility': [
                'Yoga', 'Pilates', 'Dynamic Stretching', 'Static Stretching',
                'Foam Rolling', 'Mobility Work', 'Cat-Cow Stretch',
                'Downward Dog', "Child's Pose", 'Hamstring Stretch',
                'Hip Flexor Stretch', 'Shoulder Rolls', 'Spine Twists'
            ],
            'HIIT': [
                'Burpee Intervals', 'Sprint Intervals', 'Jump Rope Intervals',
                'Mountain Climber Intervals', 'Squat Jumps', 'Box Jumps',
                'Battle Ropes', 'Kettlebell Swings', 'Medicine Ball Slams'
            ]
        }

        self.health_restrictions = {
            HealthCondition.KNEE_PAIN: [
                'Squats', 'Lunges', 'Box Jumps', 'Jump Rope',
                'Stair Climbing', 'Burpees', 'Mountain Climbers'
            ],
            HealthCondition.BACK_PAIN: [
                'Deadlifts', 'Romanian Deadlifts', 'Shoulder Press',
                'Bench Press', 'Good Mornings'
            ],
            HealthCondition.HEART_CONDITION: [
                'HIIT', 'Sprint Intervals', 'Burpee Intervals',
                'Box Jumps', 'Battle Ropes'
            ],
            HealthCondition.SHOULDER_INJURY: [
                'Pull-ups', 'Shoulder Press', 'Bench Press',
                'Face Pulls', 'Push-ups'
            ]
        }

        self.equipment_mapping = {
            'Treadmill': ['Treadmill'],
            'Cycling': ['Stationary Bike'],
            'Yoga': ['Yoga Mat'],
            'Kettlebell Swings': ['Kettlebell'],
            'Box Jumps': ['Plyo Box'],
            'Deadlifts': ['Barbell', 'Weight Plates'],
            'Squats': ['Barbell', 'Weight Plates'],
            'Swimming': ['Pool Access'],
            'Rowing': ['Rowing Machine']
        }


class WorkoutPlanner:
    def __init__(self):
        self.exercise_db = ExerciseDatabase()
        self.goal_workout_mapping = {
            'Weight Loss': {
                'primary_type': 'Cardio',
                'workout_split': {
                    'Cardio': 0.50,
                    'Strength': 0.30,
                    'HIIT': 0.20
                },
                'intensity_range': {
                    'Cardio': '65-75% max heart rate',
                    'Strength': '12-15 reps',
                    'HIIT': '30 seconds work/30 seconds rest'
                }
            },
            'Muscle Gain': {
                'primary_type': 'Strength',
                'workout_split': {
                    'Strength': 0.70,
                    'Cardio': 0.15,
                    'Flexibility': 0.15
                },
                'intensity_range': {
                    'Strength': '8-12 reps',
                    'Cardio': '20-30 minutes low intensity',
                    'Flexibility': '15-20 minutes'
                }
            },
            'Endurance': {
                'primary_type': 'Cardio',
                'workout_split': {
                    'Cardio': 0.60,
                    'Strength': 0.25,
                    'Flexibility': 0.15
                },
                'intensity_range': {
                    'Cardio': '60-70% max heart rate',
                    'Strength': '15-20 reps',
                    'Flexibility': '20-30 minutes'
                }
            },
            'Flexibility': {
                'primary_type': 'Flexibility',
                'workout_split': {
                    'Flexibility': 0.60,
                    'Strength': 0.25,
                    'Cardio': 0.15
                },
                'intensity_range': {
                    'Flexibility': '30-45 minutes',
                    'Strength': '12-15 reps',
                    'Cardio': '20-30 minutes low intensity'
                }
            }
        }

    def calculate_difficulty_modifier(self, user: UserProfile) -> float:
        """Calculate workout difficulty based on user profile"""
        base_modifier = {
            FitnessLevel.BEGINNER: 0.8,
            FitnessLevel.INTERMEDIATE: 1.1,
            FitnessLevel.ADVANCED: 1.4
        }.get(user.fitness_level, 1.0)

        # Adjust for health conditions
        if user.health_conditions:
            base_modifier *= 0.9

        return base_modifier

    def generate_workout_plan(self, user: UserProfile, weeks: int = 4) -> Dict:
        """Generate a complete workout plan based on user profile"""
        difficulty_modifier = self.calculate_difficulty_modifier(user)
        goal_data = self.goal_workout_mapping[user.goal]

        workout_plan = {
            'user_profile': user,
            'start_date': datetime.now(),
            'weeks': {}
        }

        for week in range(1, weeks + 1):
            weekly_plan = []
            week_progression = self.calculate_progression(week, difficulty_modifier)

            for day in range(user.preferred_days):
                workout_type = self.select_workout_type(goal_data['workout_split'])
                daily_workout = self.generate_daily_workout(
                    workout_type=workout_type,
                    intensity=goal_data['intensity_range'][workout_type],
                    user=user,
                    progression=week_progression
                )
                weekly_plan.append(daily_workout)

            workout_plan['weeks'][f'Week {week}'] = {
                'progression_level': week_progression,
                'workouts': weekly_plan
            }

        return workout_plan

    def calculate_progression(self, week: int, difficulty_modifier: float) -> Dict:
        """Calculate progressive overload for the week"""
        base_progression = {
            'volume_multiplier': 1 + (0.1 * (week - 1)),
            'intensity_multiplier': 1 + (0.05 * (week - 1)),
            'complexity_level': min(3, 1 + int((week - 1) / 2))
        }
        # Apply difficulty modifier
        base_progression['volume_multiplier'] *= difficulty_modifier
        base_progression['intensity_multiplier'] *= difficulty_modifier

        return base_progression

    def select_workout_type(self, workout_split: Dict[str, float]) -> str:
        """Select workout type based on split probabilities"""
        rand = random.random()
        cumulative = 0
        for workout_type, probability in workout_split.items():
            cumulative += probability
            if rand <= cumulative:
                return workout_type
        return list(workout_split.keys())[0]  # Fallback

    def generate_daily_workout(self, workout_type: str, intensity: str,
                                user: UserProfile, progression: Dict) -> Dict:
        """Generate a single day's workout"""
        exercises_pool = self.exercise_db.workout_types[workout_type].copy()

        # Apply health condition filters
        for condition in user.health_conditions:
            restricted = self.exercise_db.health_restrictions.get(condition, [])
            exercises_pool = [e for e in exercises_pool if e not in restricted]

        # Fallback if all exercises are filtered out
        if not exercises_pool:
            exercises_pool = ["Low-Impact Walking" if workout_type == "Cardio"
                              else "Bodyweight Isometric Holds"]

        num_exercises = self.calculate_num_exercises(user.fitness_level, progression)

        selected_exercises = random.sample(
            exercises_pool,
            min(num_exercises, len(exercises_pool))
        )

        # Calculate total duration
        total_duration = self.calculate_duration(workout_type, user.fitness_level)
        total_duration_min = int(total_duration.split()[0])  # Extract minutes as int
        
        formatted_exercises = []
        for i, exercise in enumerate(selected_exercises):
            formatted_exercises.append(
                self.format_exercise(
                    exercise, 
                    workout_type, 
                    progression,
                    i,  # Pass the exercise index
                    len(selected_exercises),
                    total_duration_min
                )
            )

        return {
            'type': workout_type,
            'intensity': intensity,
            'exercises': formatted_exercises,
            'duration': total_duration,
            'required_equipment': self.get_required_equipment(selected_exercises)
        }

    def calculate_num_exercises(self, fitness_level: FitnessLevel, progression: Dict) -> int:
        """Calculate number of exercises based on fitness level and progression"""
        base_exercises = {
            FitnessLevel.BEGINNER: 4,
            FitnessLevel.INTERMEDIATE: 5,
            FitnessLevel.ADVANCED: 6
        }.get(fitness_level, 3)

        return int(base_exercises * progression['volume_multiplier'])

    def format_exercise(self, exercise: str, workout_type: str, progression: Dict,
                        exercise_index: int, num_exercises: int, total_duration_min: int) -> Dict:
        """Format exercise with sets, reps, and intensity"""
        if workout_type == 'Strength':
            return {
                'name': exercise,
                'sets': int(3 * progression['volume_multiplier']),
                'reps': int(10 * progression['intensity_multiplier']),
                'rest': '60-90 seconds'
            }
        elif workout_type == 'HIIT':
            return {
                'name': exercise,
                'intervals': int(6 * progression['volume_multiplier']),
                'work_time': '30 seconds',
                'rest_time': '30 seconds'
            }
        else:
            # Calculate exact exercise durations
            # This ensures all exercises add up to exactly the total duration
            exercise_duration = total_duration_min // num_exercises
            
            # Distribute any remaining minutes to early exercises
            remainder = total_duration_min % num_exercises
            if exercise_index < remainder:
                exercise_duration += 1
                
            return {
                'name': exercise,
                'duration': f"{exercise_duration} minutes"
            }

    def calculate_duration(self, workout_type: str, fitness_level: FitnessLevel) -> str:
        """Calculate workout duration based on type and fitness level"""
        base_duration = {
            FitnessLevel.BEGINNER: 30,
            FitnessLevel.INTERMEDIATE: 45,
            FitnessLevel.ADVANCED: 60
        }.get(fitness_level, 45)

        if workout_type in ['HIIT', 'Cardio']:
            base_duration *= 0.8

        return f"{int(base_duration)} minutes"

    def get_required_equipment(self, exercises: List[str]) -> List[str]:
        """Get list of required equipment for exercises"""
        equipment = set()
        for exercise in exercises:
            if exercise in self.exercise_db.equipment_mapping:
                equipment.update(self.exercise_db.equipment_mapping[exercise])
        return list(equipment)

    def generate_daily_challenge(self, user: UserProfile, specific_date: datetime = None) -> Dict:
        """Generate a daily workout challenge for a specific date"""
        # Use current date or specified date
        date = specific_date or datetime.now()

        # Seed random with date and user for consistency
        random.seed(f"{user.age}{user.fitness_level}{date.strftime('%Y%m%d')}")

        # Calculate day number and week progression
        day = (date - datetime(2025, 1, 1)).days + 1
        week = (day - 1) // 7 + 1

        # Get user-specific parameters
        difficulty = self.calculate_difficulty_modifier(user)
        goal_data = self.goal_workout_mapping.get(user.goal, self.goal_workout_mapping['Weight Loss'])

        # Select workout type based on weighted distribution
        available_types = list(goal_data['workout_split'].keys())
        weights = [goal_data['workout_split'][t] for t in available_types]
        random.seed(f"{user.age}{user.fitness_level}{date.strftime('%Y%m%d')}{date.weekday()}")
        workout_type = random.choices(available_types, weights=weights, k=1)[0]

        # Get available exercises (filtered by health conditions)
        exercises_pool = self.exercise_db.workout_types[workout_type].copy()
        for condition in user.health_conditions:
            restricted = self.exercise_db.health_restrictions.get(condition, [])
            exercises_pool = [e for e in exercises_pool if e not in restricted]

        # Fallback if no suitable exercises
        if not exercises_pool:
            exercises_pool = ["Low-Impact Alternative"]

        # Select exercises based on fitness level
        exercise_count = {
            FitnessLevel.BEGINNER: 2,
            FitnessLevel.INTERMEDIATE: 3,
            FitnessLevel.ADVANCED: 4
        }.get(user.fitness_level, 2)

        selected_exercises = random.sample(
            exercises_pool,
            min(exercise_count, len(exercises_pool))
        )

        # Calculate total duration
        total_duration = self.calculate_duration(workout_type, user.fitness_level)
        total_duration_min = int(total_duration.split()[0])  # Extract minutes as int

        # Format exercises using the corrected approach
        progression = self.calculate_progression(week, difficulty)
        
        formatted_exercises = []
        for i, exercise in enumerate(selected_exercises):
            formatted_exercises.append(
                self.format_exercise(
                    exercise, 
                    workout_type, 
                    progression,
                    i,  # Pass the exercise index
                    len(selected_exercises),
                    total_duration_min
                )
            )

        # Day names for challenge titles
        day_name = date.strftime("%A")

        # Build challenge
        challenge = {
            'name': f"{day_name} {workout_type} Challenge",
            'date': date.strftime("%Y-%m-%d"),
            'day_of_week': day_name,
            'type': workout_type,
            'difficulty': user.fitness_level.value,
            'exercises': formatted_exercises,
            'duration': total_duration,
            'required_equipment': self.get_required_equipment(selected_exercises)
        }

        return challenge


def main():
    # Create a user profile
    user = UserProfile(
        age=45,
        height=170,
        weight=85,
        gender='Female',
        fitness_level=FitnessLevel.INTERMEDIATE,
        health_conditions=[HealthCondition.KNEE_PAIN, HealthCondition.BACK_PAIN],
        goal='Weight Loss',
        preferred_days=5  # User wants to work out 5 days per week
    )

    planner = WorkoutPlanner()

    # Generate the regular workout plan
    workout_plan = planner.generate_workout_plan(user)

    # Print example workout from the plan
    print("\n=== WEEKLY WORKOUT PLAN ===")
    week1 = workout_plan['weeks']['Week 1']
    print(f"\nProgression Level: {week1['progression_level']}")
    for i, workout in enumerate(week1['workouts'], 1):
        print(f"\nDay {i}:")
        print(f"Type: {workout['type']}")
        print(f"Duration: {workout['duration']}")
        print(f"Intensity: {workout['intensity']}")
        print("Exercises:")
        for exercise in workout['exercises']:
            if 'sets' in exercise:
                print(f"- {exercise['name']}: {exercise['sets']} sets x {exercise['reps']} reps")
            elif 'intervals' in exercise:
                print(f"- {exercise['name']}: {exercise['intervals']} intervals")
            else:
                print(f"- {exercise['name']}: {exercise['duration']}")
        if workout['required_equipment']:
            print(f"Required Equipment: {', '.join(workout['required_equipment'])}")

    # Generate and print a single daily challenge
    print("\n=== DAILY CHALLENGE FOR TODAY ===")
    daily_challenge = planner.generate_daily_challenge(user)

    print(f"\n{daily_challenge['name']} ({daily_challenge['date']})")
    print(f"Type: {daily_challenge['type']}")
    print(f"Difficulty: {daily_challenge['difficulty']}")
    print(f"Duration: {daily_challenge['duration']}")
    print("Challenge Exercises:")

    for exercise in daily_challenge['exercises']:
        if 'sets' in exercise:
            print(f"- {exercise['name']}: {exercise['sets']} sets x {exercise['reps']} reps, rest {exercise['rest']}")
        elif 'intervals' in exercise:
            print(
                f"- {exercise['name']}: {exercise['intervals']} intervals ({exercise['work_time']} work / {exercise['rest_time']} rest)")
        else:
            print(f"- {exercise['name']}: {exercise['duration']}")

    if daily_challenge['required_equipment']:
        print(f"Required Equipment: {', '.join(daily_challenge['required_equipment'])}")


if __name__ == "__main__":
    main()