import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Define a function to train the model
def train_model():
    # Load the dataset (replace this with your own dataset loading code)
    df = pd.read_csv('modified_car_details.csv')

    # Preprocess the data (replace this with your own preprocessing code)
    X = df[['company_name','year', 'km_driven','fuel','transmission','owner', 'mileage', 'engine', 'seats']]
    y = df['price']

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    return model

# Define the Streamlit app
# Define the Streamlit app
def main():
    st.title('Car Price Prediction')

    st.write('## Enter Car Details:')
    company_name = st.text_input('Company Name')
    year = st.selectbox('Year', list(range(1983, 2021)))
    km_driven = st.number_input('Kilometers Driven', step=1)
    fuel = st.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG', 'LPG'])
    transmission = st.selectbox('Transmission', ['Manual', 'Automatic'])
    owner = st.selectbox('Owner', ['First Owner', 'Second Owner', 'Third Owner', 'Fourth and Above Owner', 'Test Drive Car'])
    mileage = st.number_input('Mileage', step=None)
    engine = st.number_input('Engine', step=None)
    seats = st.selectbox('Seats', [2, 4, 5, 6, 7, 8, 9, 10, 14])


    # Check if all fields are filled
    if st.button('Predict') and company_name and year and km_driven and fuel and transmission and owner and mileage and engine and seats:
        # Create a DataFrame from user inputs
        user_data = pd.DataFrame({
            'company_name' : [company_name],
            'year': [year],
            'km_driven': [km_driven],
            'fuel' : [fuel],
            'transmission' : [transmission],
            'owner' : [owner],
            'mileage': [mileage],
            'engine': [engine],
            'seats': [seats]
        })

        # Train the model
        model = train_model()

        # Make predictions
        prediction = model.predict(user_data)

        # Display predictions
        st.write('## Predicted Price')
        st.write(f'Estimated Price: ${prediction[0]:,.2f}')

    # Add file uploader to the app
    uploaded_file = st.file_uploader('Or Upload CSV file for prediction (if preferred):', type=['csv'])

    if uploaded_file is not None:
        # Load the uploaded CSV file
        df_new = pd.read_csv(uploaded_file)

        # Train the model
        model = train_model()

        # Make predictions
        predictions = model.predict(df_new[['company_name','year', 'km_driven','fuel','transmission','owner', 'mileage', 'engine', 'seats']])

        # Display predictions
        st.write('## Predictions from CSV file')
        st.write(pd.DataFrame({'Predicted Price': predictions}))

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
