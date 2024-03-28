import streamlit as st
import pandas as pd
import requests
import datetime

# Set the API base URL as a global variable
API_BASE_URL = 'http://34.125.23.232:5001'
st.set_page_config(layout="wide")

def fetch_past_predictions(start_date, end_date):
    # API endpoint URL for fetching past predictions
    api_url = f'{API_BASE_URL}/past-predictions?start_date={start_date}&end_date={end_date}'

    try:
        # Send GET request to the API endpoint with the date range as query parameters
        response = requests.get(api_url)
        if response.status_code == 200:
            past_predictions = response.json()  # Get the past predictions from the response
            return past_predictions
        else:
            st.error(f"Failed to fetch past predictions: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching past predictions: {e}")
        return None

def upload_file(file):
    """
    Uploads a file to the FastAPI /file/ endpoint for batch prediction.
    """
    api_url = f'{API_BASE_URL}/predict/'

    # Prepare the file in the correct format for upload
    files = {'file': (file.name, file, 'multipart/form-data')}
    
    try:
        response = requests.post(api_url, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Assuming the API returns JSON that can be directly converted to a DataFrame
            predictions_json = response.json()
            return predictions_json
        else:
            st.error(f"Failed to upload file and get predictions: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None
    
# Define a function to make predictions using the API endpoint
def make_prediction(data):
    # API endpoint URL for prediction
    api_url = f'{API_BASE_URL}/predict/'

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
    mileage = st.number_input('Mileage (in kmpl)', step=0.1, format='%f')
    engine = st.number_input('Engine (in cc)', step=1)
    seats = st.selectbox('Seats', [2, 4, 5, 6, 7, 8, 9, 10, 14])
    max_power = st.number_input('Max Power (in bhp)', step=0.1, format='%f')

    if st.button('Predict'):
        if car_company_name and year and km_driven and fuel and transmission and owner and mileage and engine and seats and max_power:
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

            prediction = make_prediction(user_data)
            if prediction:
                # Assuming 'predicted_price' is the key for the prediction result
                predicted_price = prediction.get("predicted_price", "Prediction not available")
                # Append the prediction to the user_data or create a new dict for display
                display_data = user_data.copy()  # Copy to not alter the original user_data
                display_data['Predicted Price'] = predicted_price
                
                # Convert to DataFrame for display, turning the dictionary into a two-column DataFrame
                display_df = pd.DataFrame(list(display_data.items()), columns=['Feature', 'Value'])
                
                # Display the DataFrame in Streamlit
                st.write('## Prediction Result')
                st.dataframe(display_df)
            else:
                st.write("No prediction was made. Please check your input data.")
        else:
            st.error("Please fill in all the fields to make a prediction.")


    st.title('Upload file for prediction ')

    # File uploader widget
    uploaded_file = st.file_uploader('Upload CSV file here :', type=['csv'])

   # Add a "Predict" button
    if st.button('Predict on CSV file'):
        if uploaded_file is not None:
            # Call the function to upload the file and get predictions
            predictions_json = upload_file(uploaded_file)

            if predictions_json:
                # Convert the JSON response to a DataFrame
                predictions_df = pd.DataFrame(predictions_json["data"])

                # Display the DataFrame in Streamlit
                st.write('## Predictions from CSV file')
                st.dataframe(predictions_df)
        else:
            st.write("Please upload a CSV file to proceed.")

    st.title('Get Last Predicitions')

    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=30))
    end_date = st.date_input("End Date", datetime.date.today())

    if st.button('Fetch Past Predictions'):
        past_predictions = fetch_past_predictions(start_date, end_date)
        if past_predictions:
            
            # Convert the list of dictionaries to a DataFrame for display
            past_predictions_df = pd.DataFrame(past_predictions)
            st.write(past_predictions_df)

if __name__ == '__main__':
    main()