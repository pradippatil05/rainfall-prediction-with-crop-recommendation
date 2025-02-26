from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load the model and ColumnTransformer
with open('ann.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

with open('ann_transformer.pkl', 'rb') as f:
    loaded_ct = pickle.load(f)

# Load the dataset
df = pd.read_csv('yearly_data.csv')

# Define a function to process form data and make predictions
def predict_rainfall(subdivision, year):
    new_data = {
        'SUBDIVISION': [subdivision],
        'YEAR': [year]
    }

    # Convert the data into a DataFrame
    new_df = pd.DataFrame(new_data)

    # Transform the new record using the loaded column transformer
    new_transformed = loaded_ct.transform(new_df)

    # Use the loaded model to predict the rainfall for the new record
    new_prediction = loaded_model.predict(new_transformed)

    return new_prediction[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subdivision = request.form['Location']  # Changed to 'Location'
        year = int(request.form['year'])

        prediction = predict_rainfall(subdivision, year)

        return render_template('res.html', subdivision=subdivision, year=year, prediction=prediction)

    return render_template('ind.html')  # Changed to 'form.html'

if __name__ == '__main__':
    app.run(debug=True)
