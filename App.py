import streamlit as st
import pandas as pd
import requests

# Define a function to make predictions using the API endpoint
def make_prediction(data):
    # API endpoint URL for prediction
    api_url = 'http://34.125.23.232:5001/predict/'

    try:
        # Send POST request to the API endpoint with user data
        response = requests.post(api_url, json=data)
        prediction = response.json()  # Get the prediction from the response

        return prediction
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        return None

def main():
    st.title('Car Price Prediction')

    st.write('## Enter Car Details:')
    car_company_name = st.text_input('Company Name')
    year = st.selectbox('Year', list(range(1983, 2021)))
    km_driven = st.number_input('Kilometers Driven', step=1)
    fuel = st.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG', 'LPG'])
    transmission = st.selectbox('Transmission', ['Manual', 'Automatic'])
    owner = st.selectbox('Owner', ['First Owner', 'Second Owner', 'Third Owner', 'Fourth and Above Owner', 'Test Drive Car'])
    mileage = st.number_input('Mileage', step=None)
    engine = st.number_input('Engine', step=None)
    seats = st.selectbox('Seats', [2, 4, 5, 6, 7, 8, 9, 10, 14])
    max_power = st.number_input('Max Power', step=None)

    # Check if all fields are filled
    if st.button('Predict') and car_company_name and year and km_driven and fuel and transmission and owner and mileage and engine and seats:
        # Create a dictionary from user inputs
        user_data = {
            'car_company_name': car_company_name,
            'year': year,
            'km_driven': km_driven,
            'fuel': fuel,
            'transmission': transmission,
            'owner': owner,
            'mileage': mileage,
            'engine': engine,
            'seats': seats,
            'max_power': max_power
        }

        # Make API request to get predictions
        prediction = make_prediction(user_data)
        print(prediction)

    # Add file uploader to the app
    uploaded_file = st.file_uploader('Or Upload CSV file for prediction (if preferred):', type=['csv'])

    if uploaded_file is not None:
        # Load the uploaded CSV file
        df_new = pd.read_csv(uploaded_file)

        # Prepare data for API request
        api_data = df_new[['car_company_name','year', 'km_driven','fuel','transmission','owner', 'mileage', 'engine', 'seats', 'max_power']].to_dict(orient='records')

        # Make API request to get predictions for each row
        predictions = [make_prediction(row) for row in api_data]

        # Display predictions
        st.write('## Predictions from CSV file')
        st.write(pd.DataFrame({'Predicted Price': [pred["predicted_price"] for pred in predictions]}))

    # Button for past predictions
    if st.button('View Past Predictions'):
        # Load and display past predictions (replace this with your own past predictions data)
        past_predictions_data = {
            'Date': ['2022-01-01', '2022-02-01', '2022-03-01'],
            'Predicted Price': [25000, 27000, 28000]
        }
        past_predictions_df = pd.DataFrame(past_predictions_data)
        st.write('## Past Predictions')
        st.write(past_predictions_df)

if __name__ == '__main__':
    main()
