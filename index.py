import datetime
import json
from flask import Flask, render_template, request, jsonify
import joblib
import os

import requests


app = Flask(__name__)


@app.route('/')
def default_route():
    # Get the absolute path of the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the current directory with the model filename
    model_filename = os.path.join(
        current_directory, './api/rforest_model_data2.joblib')
    loaded_model = joblib.load(model_filename)
    api_key = 'Q337RWTF9APSMZZ7J6GUAZUPF'
    base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/bejaia'

    # Construct the full URL with parameters
    url = f"{base_url}?unitGroup=uk&include=days&key={api_key}&contentType=json"

    try:
        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON data from the response
            weather_data = response.json()

           # Initialize an empty list to store dictionaries
            result_list = []

            # Loop through each day in the API response
            for day in weather_data["days"][:4]:
                # Extract relevant information
                year, month, day_of_month = map(
                    int, day["datetime"].split('-'))
                temperature = day["tempmax"]
                relative_humidity = day["humidity"]
                wind_speed = day["windspeed"]
                rain = day["precip"]
                dew = day["dew"]
                condition = day['conditions']
                pres = day['pressure']

                # Create a dictionary for the current day
                day_dict = {
                    "DAY": day_of_month,
                    "MONTH": month,
                    "YEAR": year,
                    "TEMPERATURE": temperature,
                    "RAIN": rain,
                    "WS": wind_speed,
                    "PRES": pres,
                    "RH": relative_humidity,
                    "DEW POINT MAX": dew,
                    "Condition": condition
                }

                input_data = [[day_dict[feature]
                               for feature in day_dict if feature != "Condition"]]
                # Make predictions using the loaded model
                prediction = loaded_model.predict(input_data)

                # Add the prediction to the day_dict
                day_dict["PREDICTION"] = prediction.tolist()

                # Append the dictionary to the result list
                result_list.append(day_dict)

            # Print the resulting list of dictionaries
            for day_info in result_list:
                print(day_info)

            return render_template('index.html', result=result_list)

        else:
            # If the request was not successful, return an error message
            return jsonify({"error": f"Request failed with status code {response.status_code}"})

    except Exception as e:
        # Handle any exceptions that may occur during the request
        return jsonify({"error": f"An error occurred: {str(e)}"})

    return render_template('index.html', )


@app.route('/predict', methods=['POST'])
def predict():
    # Get the absolute path of the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the current directory with the model filename
    model_filename1 = os.path.join(
        current_directory, './api/final_model.joblib')
    loaded_model1 = joblib.load(model_filename1)
    model_filename2 = os.path.join(
        current_directory, './api/rforest_model_data2.joblib')
    loaded_model2 = joblib.load(model_filename2)

    # Default values (average of some attributes)
    default_values = {
        'FFMC': 77.887705,
        'DMC': 14.673361,
        'DC': 49.288115,
        'ISI': 4.759836,
        'BUI': 16.673361,
        'FWI': 7.04918
    }
    # this counter is to decide wethere we will use the first or the second model
    # based on the number of empty cells in FWI System
    counter = 0
    try:
        # Get the input data from the JSON request
        data = request.get_json()
        feature_dict = {}
        for entry in data:
            if entry['value'] == '--':
                feature_dict[entry['name'].upper()] = default_values.get(
                    entry['name'].upper(), 1)
                counter = counter + 1
            else:
                feature_dict[entry['name'].upper()] = float(entry['value'])

        # Now, feature_dict contains the required features with integer values or 1 for '--'
        print(feature_dict)
        print(counter)
        if counter <= 3:
            feature_dict.pop('DEW')
            feature_dict.pop('PRES')
            # use the first model
            print(feature_dict)
            # Specify the order of features based on your model training
            feature_order = ['TEMPERATURE', 'RH', 'WS',
                             'RAIN', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI', 'FWI']

            # Create a list of feature values in the specified order
            input_data = [[feature_dict[feature] for feature in feature_order]]
            print(input_data)
            # Make predictions using the loaded model
            prediction = loaded_model1.predict(input_data)
            print(prediction.tolist())
            print('hi')
            return jsonify({
                'feature_dict': feature_dict,
                'model': 1,
                'prediction': prediction.tolist()
            })

        else:
            # use the second model
            feature_order = ['DAY', 'MONTH', 'YEAR',
                             'TEMPERATURE', 'RH', 'WS', 'PRES', 'RAIN', 'DEW']
            feature_dict.pop('FFMC')
            feature_dict.pop('DMC')
            feature_dict.pop('DC')
            feature_dict.pop('ISI')
            feature_dict.pop('BUI')
            feature_dict.pop('FWI')

            feature_dict['YEAR'] = 2014
            feature_dict['MONTH'] = 2
            feature_dict['DAY'] = 13

            input_data = [[feature_dict[feature] for feature in feature_order]]
            print(input_data)
            # Make predictions using the loaded model
            prediction = loaded_model2.predict(input_data)
            print(prediction.tolist())
            print('hi')
            return jsonify({
                'feature_dict': feature_dict,
                'model': 2,
                'prediction': prediction.tolist()
            })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/result')
def result():
    # Retrieve parameters from the URL
    feature_dict = request.args.get('feature_dict')
    model = request.args.get('model')
    prediction = request.args.get('prediction')

    # Convert JSON strings to Python dictionaries
    feature_dict = json.loads(feature_dict)
    prediction = json.loads(prediction)

    # Render the result template with the provided data
    return render_template('result.html', feature_dict=feature_dict, model=model, prediction=prediction)


@app.route('/10days')
def get_weather_data():
    # Get the absolute path of the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the current directory with the model filename
    model_filename = os.path.join(
        current_directory, './api/rforest_model_data2.joblib')
    loaded_model = joblib.load(model_filename)
    api_key = 'Q337RWTF9APSMZZ7J6GUAZUPF'
    base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/bejaia'

    # Construct the full URL with parameters
    url = f"{base_url}?unitGroup=uk&include=days&key={api_key}&contentType=json"

    try:
        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON data from the response
            weather_data = response.json()

           # Initialize an empty list to store dictionaries
            result_list = []

            # Loop through each day in the API response
            for day in weather_data["days"]:
                # Extract relevant information
                year, month, day_of_month = map(
                    int, day["datetime"].split('-'))
                temperature = day["tempmax"]
                relative_humidity = day["humidity"]
                wind_speed = day["windspeed"]
                rain = day["precip"]
                dew = day["dew"]
                condition = day['conditions']
                pres = day['pressure']

                # Create a dictionary for the current day
                day_dict = {
                    "DAY": day_of_month,
                    "MONTH": month,
                    "YEAR": year,
                    "TEMPERATURE": temperature,
                    "RAIN": rain,
                    "WS": wind_speed,
                    "PRES": pres,
                    "RH": relative_humidity,
                    "DEW POINT MAX": dew,
                    "Condition": condition
                }

                input_data = [[day_dict[feature]
                               for feature in day_dict if feature != "Condition"]]
                # Make predictions using the loaded model
                prediction = loaded_model.predict(input_data)

                # Add the prediction to the day_dict
                day_dict["PREDICTION"] = prediction.tolist()

                # Append the dictionary to the result list
                result_list.append(day_dict)

            # Print the resulting list of dictionaries
            for day_info in result_list:
                print(day_info)

            return render_template('10days.html', result=result_list)

        else:
            # If the request was not successful, return an error message
            return jsonify({"error": f"Request failed with status code {response.status_code}"})

    except Exception as e:
        # Handle any exceptions that may occur during the request
        return jsonify({"error": f"An error occurred: {str(e)}"})
