from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import dateutil.parser
from Exercise import UserProfile, WorkoutPlanner, FitnessLevel, HealthCondition

app = Flask(__name__)
planner = WorkoutPlanner()

# Standardized error responses
def error_response(message, status_code=400):
    """Create a standardized error response"""
    return jsonify({
        'error': True,
        'message': message
    }), status_code

# Error handling
@app.errorhandler(400)
def bad_request(error):
    return error_response(str(error), 400)

@app.errorhandler(404)
def not_found(error):
    return error_response(str(error), 404)

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    """Get all available exercises"""
    exercise_type = request.args.get('type')
    if exercise_type:
        # Make sure type matches exactly what's in exercise_db.workout_types
        # (Cardio, Strength, Flexibility, HIIT)
        if exercise_type in planner.exercise_db.workout_types:
            return jsonify({
                'exercises': planner.exercise_db.workout_types[exercise_type]
            })
    return jsonify({
        'exercises': planner.exercise_db.workout_types
    })

@app.route('/api/workout-types', methods=['GET'])
def get_workout_types():
    """Get available workout types and their exercises"""
    return jsonify({
        'workout_types': list(planner.exercise_db.workout_types.keys())
    })

@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    """Get equipment mappings"""
    return jsonify({
        'equipment_mapping': planner.exercise_db.equipment_mapping
    })

@app.route('/api/goals', methods=['GET'])
def get_goals():
    """Get available fitness goals and their workout splits"""
    return jsonify({
        'goals': list(planner.goal_workout_mapping.keys())
    })

def standardize_fitness_level(level):
    """Convert any fitness level string to FitnessLevel enum"""
    if isinstance(level, FitnessLevel):
        return level
        
    level_map = {
        "beginner": FitnessLevel.BEGINNER,
        "intermediate": FitnessLevel.INTERMEDIATE, 
        "advanced": FitnessLevel.ADVANCED
    }
    
    if isinstance(level, str):
        level_lower = level.lower().strip()
        return level_map.get(level_lower, FitnessLevel.INTERMEDIATE)
    
    return FitnessLevel.INTERMEDIATE

def standardize_health_conditions(conditions):
    """Standardize health conditions to match HealthCondition enum"""
    if not conditions:
        return []
    
    if isinstance(conditions, str):
        conditions = [conditions]
    
    condition_map = {
        "knee pain": HealthCondition.KNEE_PAIN,
        "knee": HealthCondition.KNEE_PAIN,
        "back pain": HealthCondition.BACK_PAIN,
        "back": HealthCondition.BACK_PAIN,
        "heart condition": HealthCondition.HEART_CONDITION,
        "heart": HealthCondition.HEART_CONDITION,
        "shoulder injury": HealthCondition.SHOULDER_INJURY,
        "shoulder": HealthCondition.SHOULDER_INJURY
    }
    
    standardized = []
    for condition in conditions:
        if isinstance(condition, str):
            condition_lower = condition.lower().strip()
            if condition_lower in condition_map:
                standardized.append(condition_map[condition_lower])
            else:
                # Try to match directly with enum values
                try:
                    standardized.append(HealthCondition(condition))
                except ValueError:
                    # Skip invalid conditions
                    pass
        elif isinstance(condition, HealthCondition):
            standardized.append(condition)
    
    return standardized

def standardize_goal(goal):
    """Make sure goal matches one of the keys in goal_workout_mapping"""
    if not goal:
        return "Weight Loss"  # Default
        
    goal_map = {
        "weight_loss": "Weight Loss",
        "weightloss": "Weight Loss",
        "weight loss": "Weight Loss",
        "muscle_gain": "Muscle Gain",
        "musclegain": "Muscle Gain", 
        "muscle gain": "Muscle Gain",
        "endurance": "Endurance",
        "flexibility": "Flexibility"
    }
    
    if isinstance(goal, str):
        goal_lower = goal.lower().strip()
        return goal_map.get(goal_lower, goal)
    
    return goal

def parse_date(date_str):
    """Parse and validate a date string"""
    try:
        return dateutil.parser.parse(date_str)
    except ValueError:
        raise ValueError("Date should be in ISO format (YYYY-MM-DD)")

def validate_user_data(data):
    """Validate user data and standardize formats"""
    # Validate required fields
    required_fields = ['age', 'height', 'weight', 'gender', 'fitness_level',
                       'goal', 'preferred_days']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Type checking
    try:
        data['age'] = int(data['age'])
        data['height'] = float(data['height'])
        data['weight'] = float(data['weight'])
    except (ValueError, TypeError):
        return False, "Age must be an integer, height and weight must be numeric"
    
    # Standardize values to match Exercise.py expectations
    data['fitness_level'] = standardize_fitness_level(data['fitness_level'])
    data['health_conditions'] = standardize_health_conditions(data.get('health_conditions', []))
    data['goal'] = standardize_goal(data['goal'])
    
    # Handle preferred_days - needs to be an integer for UserProfile
    if isinstance(data['preferred_days'], list):
        data['preferred_days'] = len(data['preferred_days'])
    elif not isinstance(data['preferred_days'], int):
        try:
            data['preferred_days'] = int(data['preferred_days'])
        except (ValueError, TypeError):
            data['preferred_days'] = 3  # Default to 3 days
    
    return True, data

@app.route('/api/generate-plan', methods=['POST'])
def generate_workout_plan():
    """Generate a workout plan based on user profile"""
    try:
        data = request.get_json()
        
        # Validate and standardize data
        is_valid, result = validate_user_data(data)
        if not is_valid:
            return error_response(result)
        
        data = result  # Update with standardized data

        # Create user profile
        user = UserProfile(
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender'],
            fitness_level=data['fitness_level'],
            health_conditions=data['health_conditions'],
            goal=data['goal'],
            preferred_days=data['preferred_days']
        )

        # Generate plan
        weeks = data.get('weeks', 4)  # Default to 4 weeks if not specified
        workout_plan = planner.generate_workout_plan(user, weeks=weeks)

        return jsonify({
            'workout_plan': workout_plan
        })

    except Exception as e:
        return error_response(f"Failed to generate workout plan: {str(e)}")

@app.route('/api/calculate-difficulty', methods=['POST'])
def calculate_difficulty():
    """Calculate workout difficulty based on user profile"""
    try:
        data = request.get_json()
        
        # Validate and standardize data
        is_valid, result = validate_user_data(data)
        if not is_valid:
            return error_response(result)
        
        data = result  # Update with standardized data
        
        user = UserProfile(
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender'],
            fitness_level=data['fitness_level'],
            health_conditions=data['health_conditions'],
            goal=data['goal'],
            preferred_days=data['preferred_days']
        )

        difficulty = planner.calculate_difficulty_modifier(user)
        return jsonify({
            'difficulty_modifier': difficulty
        })

    except Exception as e:
        return error_response(f"Failed to calculate difficulty: {str(e)}")

@app.route('/api/daily-challenge', methods=['POST'])
def get_daily_challenge():
    """Generate a daily workout challenge based on user profile and optional date"""
    try:
        data = request.get_json()
        
        # Validate and standardize data
        is_valid, result = validate_user_data(data)
        if not is_valid:
            return error_response(result)
        
        data = result  # Update with standardized data

        # Create user profile
        user = UserProfile(
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender'],
            fitness_level=data['fitness_level'],
            health_conditions=data['health_conditions'],
            goal=data['goal'],
            preferred_days=data['preferred_days']
        )

        # Check if specific date is provided
        specific_date = None
        if 'date' in data and data['date']:
            try:
                specific_date = parse_date(data['date'])
            except ValueError as e:
                return error_response(str(e))

        # Generate daily challenge
        daily_challenge = planner.generate_daily_challenge(user, specific_date)

        return jsonify({
            'daily_challenge': daily_challenge
        })

    except Exception as e:
        return error_response(f"Failed to generate daily challenge: {str(e)}")

@app.route('/api/daily-challenges-batch', methods=['POST'])
def get_daily_challenges_batch():
    """Generate multiple daily challenges for a date range"""
    try:
        data = request.get_json()
        
        # Validate and standardize user data
        is_valid, result = validate_user_data(data)
        if not is_valid:
            return error_response(result)
        
        data = result  # Update with standardized data
        
        # Validate date fields
        if 'start_date' not in data or 'end_date' not in data:
            return error_response("Missing required fields: start_date and end_date")

        # Parse dates
        try:
            start_date = parse_date(data['start_date'])
            end_date = parse_date(data['end_date'])
        except ValueError as e:
            return error_response(str(e))

        if start_date > end_date:
            return error_response("Start date must be before or equal to end date")

        # Create user profile
        user = UserProfile(
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            gender=data['gender'],
            fitness_level=data['fitness_level'],
            health_conditions=data['health_conditions'],
            goal=data['goal'],
            preferred_days=data['preferred_days']
        )

        # Generate a challenge for each date in the range
        challenges = []
        current_date = start_date
        days_limit = 31  # Limit to prevent excessive processing
        day_count = 0

        while current_date <= end_date and day_count < days_limit:
            challenge = planner.generate_daily_challenge(user, current_date)
            challenges.append(challenge)

            # Move to next day (safer date increment)
            current_date = current_date + timedelta(days=1)
            day_count += 1

        return jsonify({
            'daily_challenges': challenges,
            'count': len(challenges)
        })

    except Exception as e:
        return error_response(f"Failed to generate daily challenges batch: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)