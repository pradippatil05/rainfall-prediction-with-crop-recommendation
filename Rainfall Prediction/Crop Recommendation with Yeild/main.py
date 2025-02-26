from flask import Flask, render_template, request, redirect, url_for, session
import requests as requests
import pickle
from CropApi import CROPAPI
import pandas as pd
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)
location_names = {
    '1': 'ANDAMAN & NICOBAR ISLANDS',
    '2': 'ARUNACHAL PRADESH',
    '3': 'ASSAM & MEGHALAYA',
    '4': 'NAGA MANI MIZO TRIPURA',
    '5': 'SUB HIMALAYAN WEST BENGAL & SIKKIM',
    '6': 'GANGETIC WEST BENGAL',
    '7': 'ORISSA',
    '8': 'JHARKHAND',
    '9': 'BIHAR',
    '10': 'EAST UTTAR PRADESH',
    '11': 'WEST UTTAR PRADESH',
    '12': 'UTTARAKHAND',
    '13': 'HARYANA DELHI & CHANDIGARH',
    '14': 'PUNJAB',
    '15': 'HIMACHAL PRADESH',
    '16': 'JAMMU & KASHMIR',
    '17': 'WEST RAJASTHAN',
    '18': 'EAST RAJASTHAN',
    '19': 'WEST MADHYA PRADESH',
    '20': 'EAST MADHYA PRADESH',
    '21': 'GUJARAT REGION',
    '22': 'SAURASHTRA & KUTCH',
    '23': 'KONKAN',
    '24': 'MADHYA MAHARASHTRA',
    '25': 'MATATHWADA',
    '26': 'VIDARBHA',
    '27': 'CHHATTISGARH',
    '28': 'COASTAL ANDHRA PRADESH',
    '29': 'TELANGANA ',
    '30': 'RAYALSEEMA',
    '31': 'TAMIL NADU',
    '32': 'COASTAL KARNATAKA',
    '33': 'NORTH INTERIOR KARNATAKA',
    '34': 'SOUTH INTERIOR KARNATAKA',
    '35': 'KERALA',
    '36': 'LAKSHADWEEP',
}

month_names = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}

crop_recommendation_model = pickle.load(open("cropRecommdendationModel.pkl", "rb"))
API_KEY_OPEN_WEATHER = "4c61f798e1507fb0f06b70da4c7d41c8"
cropApi = CROPAPI()
api_data = []
Current_location=None
Nitrogen = 0

with open("Random_model.pickle", 'rb') as file:
    loaded_model = pickle.load(file)
    print(loaded_model.predict([[2045,9]]))
print("Model unpickled successfully!")

# Route for the main index page
@app.route('/')
def home():
    return render_template("index.html")


# Route for the button to navigate to the rainfall prediction page
@app.route('/go_to_rainfall_prediction')
def go_to_rainfall_prediction():
    return redirect(url_for('rainfall_prediction'))


# Route for the soil data input form
@app.route("/get_soil_data", methods=['GET', 'POST'])
def get_soil_data():
    if request.method == "POST":
        n = request.form.get('n')
        p = request.form.get('p')
        k = request.form.get('k')
        ph = request.form.get('ph')
        temperature = request.form.get('temp')
        humidity = request.form.get('humidity')
        rainfall = request.form.get('RainFall')
        recommended_crop = crop_recommendation_model.predict(pd.DataFrame([[float(n), float(p), float(k), float(temperature), float(humidity), float(ph), float(rainfall)]], columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']))[0]
        return render_template("soil_data_input.html", crop=recommended_crop, result=1)
    return render_template("soil_data_input.html", crop="", result=0)


# Route for the location input form
@app.route('/location', methods=['GET','POST'])
def location():
    print(Nitrogen)
    if request.method == "POST":
        properties = ['Nitrogen', 'Phosphorus', 'Potassium', 'PH Level', 'Temperature', 'Humidity', 'RainFall ']
        p = request.form.get('p')
        k = request.form.get('k')
        ph = request.form.get('ph')
        rainfall = request.form.get('RainFall')
        
        if len(api_data) > 0:
            print(p, k, ph, rainfall, api_data[0],api_data[1])
            recommended_crop = crop_recommendation_model.predict(
                pd.DataFrame([[float(Nitrogen), float(p), float(k), float(api_data[0]), float(api_data[1]), float(ph), float(rainfall)]],
                         columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']))[0]
            print(recommended_crop)
            values = [float(Nitrogen), float(p), float(k), float(api_data[0]), float(api_data[1]), float(ph), float(rainfall)]
            return render_template('Location.html', valuesLength=range(len(values)), values=values, Location=Current_location, result=1, properties=properties, crop=recommended_crop)
    return render_template('Location.html', values=0 ,result=0)


# Route for the rainfall prediction form
@app.route("/rainfallPrediction", methods=['GET', 'POST'])
def rainfallPrediction():
    if request.method == 'POST':
        year = int(request.form.get('year'))
        month_value = int(request.form.get('Month'))
        location_value = request.form.get('Location')

        location_name = location_names.get(location_value, 'Unknown Location')
        month_name = month_names.get(str(month_value), 'Unknown Month')

        session['selected_location'] = location_name
        session['selected_month'] = month_name

        predicted_value = loaded_model.predict([[year, month_value]])[0]

        return redirect(url_for('showResult', year=year, month=month_name, predicted_value=predicted_value))

    return render_template("predict.html")

# Route for showing the result of rainfall prediction
@app.route("/result")
def showResult():
    year = request.args.get('year')
    month = session.get('selected_month', 'Unknown Month')
    location = session.get('selected_location', 'Unknown Location')
    predicted_value = request.args.get('predicted_value')

    return render_template("result.html", year=year, month=month, location=location, predicted_value=predicted_value)

# Load the model and ColumnTransformer for rainfall prediction
with open('ann.pkl', 'rb') as f:
    loaded_model_rainfall = pickle.load(f)

with open('ann_transformer.pkl', 'rb') as f:
    loaded_ct_rainfall = pickle.load(f)

df_rainfall = pd.read_csv('yearly_data.csv')

def predict_rainfall(subdivision, year):
    new_data = {
        'SUBDIVISION': [subdivision],
        'YEAR': [year]
    }

    new_df = pd.DataFrame(new_data)

    new_transformed = loaded_ct_rainfall.transform(new_df)

    new_prediction = loaded_model_rainfall.predict(new_transformed)

    return new_prediction[0]

# Route for the rainfall prediction page
@app.route('/rain', methods=['GET', 'POST'])
def rainfall_prediction():
    if request.method == 'POST':
        subdivision = request.form['Location']
        year = int(request.form['year'])

        prediction = predict_rainfall(subdivision, year)

        return render_template('res.html', subdivision=subdivision, year=year, prediction=prediction)

    return render_template('ind.html')

# Route for the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True, port=2000)
