import streamlit as st
import pandas as pd
import requests
import datetime
import json 
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
    

def main():
        # Streamlit app layout
    st.title('Vehicle Price Prediction')

    # Form for user input
    with st.form(key='vehicle_form'):
        year = st.number_input('Year', min_value=1980, max_value=2024, step=1)
        km_driven = st.number_input('Kilometers Driven', min_value=0)
        seats = st.number_input('Seats', min_value=1, max_value=10, step=1)
        mileage = st.number_input('Mileage (km/l)')
        engine = st.number_input('Engine (CC)')
        max_power = st.number_input('Max Power (bhp)')
        car_company_name = st.text_input('Car Company Name')
        fuel = st.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG', 'LPG', 'Electric'])
        transmission = st.selectbox('Transmission', ['Manual', 'Automatic'])
        owner = st.selectbox('Owner Type', ['First', 'Second', 'Third', 'Fourth & Above'])
        
        submit_button = st.form_submit_button(label='Predict Price')

    # POST request to the endpoint
    if submit_button:
        vehicle_data = {
            "year": year,
            "km_driven": km_driven,
            "seats": seats,
            "mileage": mileage,
            "engine": engine,
            "max_power": max_power,
            "car_company_name": car_company_name,
            "fuel": fuel,
            "transmission": transmission,
            "owner": owner
        }

        # The server expects a form field named 'vehicle_data' with a JSON string as its value
        form_data = {
            'vehicle_data': json.dumps(vehicle_data),  # Convert dict to JSON string
        }

        # Endpoint URL
        api_url = f'{API_BASE_URL}/predict/'

        # Making the POST request with form data
        response = requests.post(api_url, data=form_data)  # Note the use of 'data' instead of 'files'
        
        if response.status_code == 200:
            # Displaying the prediction result
            prediction = response.json()
           

            # Assuming form_data.get('vehicle_data') returns a JSON string of vehicle_data
            vehicle_data_json_str = form_data.get('vehicle_data')

            # Convert JSON string back to dictionary
            vehicle_data_dict = json.loads(vehicle_data_json_str)

            # Convert the dictionary to a DataFrame
            # Since the dictionary represents a single record, you need to wrap it in a list to create a DataFrame
            display_data = pd.DataFrame([vehicle_data_dict])
            print('display_data is ', display_data) # Copy to not alter the original user_data
            display_data['Predicted Price'] = prediction.get("predicted_price")
            
            # Convert to DataFrame for display, turning the dictionary into a two-column DataFrame
            #display_df = pd.DataFrame(list(display_data.items()), columns=['Feature', 'Value'])
            
            # Display the DataFrame in Streamlit
            st.write('## Prediction Result')
            st.dataframe(display_data)
            #st.success(f'Predicted Vehicle Price: {prediction.get("predicted_price")}')
        else:
            # Displaying error message
            st.error(f'Failed to predict price. Error: {response.text}')

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

    st.title('Past predictions ')

    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=30))
    end_date = st.date_input("End Date", datetime.date.today())

    if st.button('Fetch Past Predictions'):
        past_predictions = fetch_past_predictions(start_date, end_date)
        
        if past_predictions:
            # Convert the list of dictionaries to a DataFrame for display
            past_predictions_df = pd.DataFrame(past_predictions)
            
            st.write("The length of the dataframe is ", len(past_predictions_df))
            st.dataframe(past_predictions_df.head(20))




if __name__ == '__main__':
    main()