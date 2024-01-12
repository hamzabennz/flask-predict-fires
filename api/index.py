from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def default_route():
    if request.method == 'GET':
        return jsonify({'message': 'Welcome to the default route!'})

    elif request.method == 'POST':
        return jsonify({'message': 'Received a POST request at the default route.'})

    else:
        return jsonify({'error': 'Unsupported method'}), 405


# Load the pre-trained model
model_filename = 'final_model.joblib'
loaded_model = joblib.load(model_filename)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the JSON request
        data = request.get_json()

        # Ensure all required features are present
        required_features = ['TEMPERATURE', 'RH', 'WS',
                             'RAIN', 'FFMC', 'DMC', 'DC', 'ISI', 'BUI', 'FWI']
        if not all(feature in data for feature in required_features):
            return jsonify({'error': 'Missing required features'}), 400

        # Prepare the input data for prediction
        input_data = [[data[feature] for feature in required_features]]

        # Make predictions using the loaded model
        prediction = loaded_model.predict(input_data)

        # Return the prediction as JSON
        return jsonify({'prediction': prediction.tolist()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

