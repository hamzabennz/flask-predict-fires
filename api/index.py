from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
