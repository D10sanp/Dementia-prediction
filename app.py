import pickle
import numpy as np
import requests
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Load the trained model, label encoder, and scaler
with open('models/svm_model.pkl', 'rb') as model_file:
    svm_model = pickle.load(model_file)

with open('models/label_encoder.pkl', 'rb') as label_encoder_file:
    label_encoder = pickle.load(label_encoder_file)

with open('models/scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

def get_diet_recommendation(diet_type="Brain Health"):
    # Spoonacular API endpoint for recipe search
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    # Spoonacular API key - replace with your actual API key
    api_key = "7a083daaaa3947b392f48c534f5d2e85"  # Replace with your Spoonacular API key

    params = {
        'query': diet_type,  # Search for recipes related to the diet type
        'number': 3,         # Number of recipes to return
        'apiKey': api_key    # Spoonacular API key
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    
    # Print out the full response for debugging
    print(f"API Response Code: {response.status_code}")
    print(f"API Response Body: {response.text}")
    
    data = response.json()
    
    # Check if the response is valid
    if response.status_code == 200 and 'results' in data:
        # Extract the top 3 recipes from the response
        recipes = data['results'][:3]
        recommendations = [recipe['title'] for recipe in recipes]
        
        # Return the recommendations as a string
        return ', '.join(recommendations)
    else:
        return "Sorry, we couldn't fetch diet recommendations at the moment."
    
    
    

# Home route - Display the form
@app.route('/')
def index():
    return render_template('index.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    # Extract input data from the form
    diabetic = int(request.form['diabetic'])
    alcohol_level = int(request.form['alcohol_level'])
    heart_rate = float(request.form['heart_rate'])
    blood_oxygen_level = float(request.form['blood_oxygen_level'])
    body_temperature = float(request.form['body_temperature'])
    weight = float(request.form['weight'])
    age = int(request.form['age'])
    gender = int(request.form['gender'])
    family_history = int(request.form['family_history'])
    smoking_status = int(request.form['smoking_status'])
    apoe_e4 = int(request.form['apoe_e4'])
    physical_activity = int(request.form['physical_activity'])
    depression_status = int(request.form['depression_status'])
    cognitive_test_scores = float(request.form['cognitive_test_scores'])
    medication_history = int(request.form['medication_history'])
    nutrition_diet = int(request.form['nutrition_diet'])
    sleep_quality = int(request.form['sleep_quality'])
    chronic_health_conditions = int(request.form['chronic_health_conditions'])

    # Prepare the input data
    input_data = np.array([[
        diabetic, alcohol_level, heart_rate, blood_oxygen_level, body_temperature, weight, age, gender,
        family_history, smoking_status, apoe_e4, physical_activity, depression_status, cognitive_test_scores,
        medication_history, nutrition_diet, sleep_quality, chronic_health_conditions
    ]])

    # Reshape and scale the input data
    input_data = input_data.reshape(1, -1)
    input_data_scaled = scaler.transform(input_data)

    # Predict using the trained model
    prediction = svm_model.predict(input_data_scaled)
    prediction_label = label_encoder.inverse_transform(prediction)[0]

    # Determine the prediction message
    if prediction_label == 1:
        prediction_text = "Dementia likely detected. Please consult a doctor."
        diet_type = "Brain Health"  # Suggest a brain health diet
    else:
        prediction_text = "No signs of dementia detected."
        diet_type = "Mediterranean"  # Suggest a Mediterranean diet for general health

    # Get diet recommendations using the API
    diet_recommendation = get_diet_recommendation(diet_type)

    # Redirect to result.html and pass prediction result and diet recommendations
    return redirect(url_for('result', prediction_text=prediction_text, diet_recommendation=diet_recommendation))

# Result route - Display the prediction result and diet recommendation
@app.route('/result')
def result():
    prediction_text = request.args.get('prediction_text')
    diet_recommendation = request.args.get('diet_recommendation')
    
    return render_template('result.html', prediction_text=prediction_text, diet_recommendation=diet_recommendation)

if __name__ == "__main__":
    app.run(debug=True)
