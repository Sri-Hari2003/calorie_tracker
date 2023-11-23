from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Replace these values with your MySQL server information
db_host = "localhost"
db_user = "root"
db_password = "7619662801"
db_database = "calorie_tracker"

# Establish a connection to the MySQL server
db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_database
)

# Function to execute SQL queries
def execute_query(query, values=None, fetchall=False):
    cursor = db_connection.cursor(dictionary=True)
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    result = cursor.fetchall() if fetchall else cursor.fetchone()
    cursor.close()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user', methods=['POST'])
def user():
    username = request.form['username']
    maintenance_calories = int(request.form['maintenance_calories'])

    # Check if the user already exists
    user_query = "SELECT user_id FROM users WHERE username = %s"
    existing_user = execute_query(user_query, (username,))

    if existing_user:
        user_id = existing_user['user_id']
    else:
        # Insert a new user
        insert_user_query = "INSERT INTO users (username, maintenance_calories) VALUES (%s, %s)"
        execute_query(insert_user_query, (username, maintenance_calories))
        user_id = execute_query("SELECT LAST_INSERT_ID() AS user_id")['user_id']

    return redirect(url_for('log_food', user_id=user_id))

@app.route('/log_food/<int:user_id>', methods=['GET', 'POST'])
@app.route('/log_food/<int:user_id>', methods=['GET', 'POST'])
def log_food(user_id):
    total_protein = 0  # Initialize with default value
    total_carbs = 0    # Initialize with default value
    total_fat = 0      # Initialize with default value
    total_calories_consumed = 0  # Initialize with default value

    if request.method == 'POST':
        food_name = request.form['food_name']

        # Fetch nutritional information for the entered food item
        food_query = "SELECT protein, carbs, fat, total_calories FROM food WHERE food_name = %s"
        food_info = execute_query(food_query, (food_name,))

        if food_info:
            protein = food_info['protein']
            carbs = food_info['carbs']
            fat = food_info['fat']
            total_calories = food_info['total_calories']

            # Calculate total macros and calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
            total_calories_consumed += total_calories

    # Fetch user information and daily calories entries
    user_info_query = "SELECT username, maintenance_calories FROM users WHERE user_id = %s"
    user_info = execute_query(user_info_query, (user_id,))

    daily_calories_query = "SELECT date, calories_consumed, calories_over_maintenance FROM daily_calories WHERE user_id = %s ORDER BY date DESC"
    daily_calories_entries = execute_query(daily_calories_query, (user_id,), fetchall=True)

    return render_template('log_food.html', user_info=user_info, daily_calories_entries=daily_calories_entries,
                           total_protein=total_protein, total_carbs=total_carbs, total_fat=total_fat,
                           total_calories_consumed=total_calories_consumed)

    if request.method == 'POST':
        food_name = request.form['food_name']

        # Fetch nutritional information for the entered food item
        food_query = "SELECT protein, carbs, fat, total_calories FROM food WHERE food_name = %s"
        food_info = execute_query(food_query, (food_name,))

        if food_info:
            protein = food_info['protein']
            carbs = food_info['carbs']
            fat = food_info['fat']
            total_calories = food_info['total_calories']
        else:
            # Default values if food information is not found
            protein = 0
            carbs = 0
            fat = 0
            total_calories = 0

        # Calculate total macros and calories
        total_protein = protein  # You can accumulate these values based on user input
        total_carbs = carbs
        total_fat = fat
        total_calories_consumed = total_calories  # You can accumulate these values based on user input

    # Fetch user information and daily calories entries
    user_info_query = "SELECT username, maintenance_calories FROM users WHERE user_id = %s"
    user_info = execute_query(user_info_query, (user_id,))

    daily_calories_query = "SELECT date, calories_consumed, calories_over_maintenance FROM daily_calories WHERE user_id = %s ORDER BY date DESC"
    daily_calories_entries = execute_query(daily_calories_query, (user_id,), fetchall=True)

    return render_template('log_food.html', user_info=user_info, daily_calories_entries=daily_calories_entries,
                           total_protein=total_protein, total_carbs=total_carbs, total_fat=total_fat,
                           total_calories_consumed=total_calories_consumed)

if __name__ == '__main__':
    app.run(debug=True)
