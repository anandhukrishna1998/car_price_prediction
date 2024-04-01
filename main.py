from typing import List, Optional
import sys
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn
from car_price.inference import make_predictions
import pandas as pd
from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException ,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import io
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sql_app.repositories import CarDetailsRepo
from fastapi import File, UploadFile
from typing import List
from datetime import date
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
from typing import Optional
from pydantic import BaseModel
import sql_app.models as models
import sql_app.schemas as schemas
from db import get_db, engine



app = FastAPI(title="Car Price Prediction",
              description=" Swagger at 5001 and Sqlalchemy orm used" )
models.Base.metadata.create_all(bind=engine)


@app.get("/past-predictions")
async def past_predictions(
    start_date: date = Query(..., description="The start date of the query range"),
    end_date: date = Query(..., description="The end date of the query range"),
    db: Session = Depends(get_db)
):
    try:

        predictions = CarDetailsRepo.get_by_date_range(db, start_date, end_date)
        data = [{
            'year': item.year,
            'km_driven': item.km_driven,
            'seats': item.seats,
            'mileage': item.mileage,
            'engine': item.engine,
            'max_power': item.max_power,
            'car_company_name': item.car_company_name,
            'fuel': item.fuel,
            'transmission': item.transmission,
            'owner': item.owner,
            'predicted_price': item.predicted_price,
            'timestamp': item.timestamp
        } for item in predictions]

        # Convert the list of dictionaries into a DataFrame
        df = pd.DataFrame(data)
        df_dict = df.to_dict(orient='records')
        if not predictions:
            # If no data is found, return a custom message
            return JSONResponse(content={"message": "There is no data in between this range"}, status_code=404)
        return df_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/")
async def make_prediction(vehicle_data: Optional[str] = Form(None), 
                          file: Optional[UploadFile] = File(None), 
                          db: Session = Depends(get_db)):
    if vehicle_data is None and file is None:
        raise HTTPException(status_code=400, detail="No input data or file provided.")
    
    try:
        if vehicle_data:
            print(vehicle_data)
            print(type(vehicle_data))
            vehicle_data = json.loads(vehicle_data)
            vehicle_dict = vehicle_data
            df = pd.DataFrame([vehicle_dict])
            predictions = make_predictions(df)
            today = pd.to_datetime('today').date()
            df['predicted_price'] = predictions
            df['timestamp'] = today
            df.to_sql('car_details', engine, if_exists='append', index=False)
            predicted_price_str = str(predictions[0])
            print(predicted_price_str)
            return {"predicted_price": predicted_price_str}
        elif file:
            print("here")
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
            contents = await file.read()
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            print(len(df))
            predictions = make_predictions(df)
            today = pd.to_datetime('today').date()
            df['predicted_price'] = predictions
            df['timestamp'] = today
            print(df.head())
            df =df[["year", "km_driven",
                        "seats", "mileage", "engine",
                        "max_power","car_company_name",
                            "fuel", 
                            "transmission", "owner","predicted_price","timestamp"]]
            df.to_sql('car_details', engine, if_exists='append', index=False)
            df['timestamp'] = df['timestamp'].astype(str) 

            # Convert DataFrame to dictionary for JSON response
            df_dict = df.to_dict(orient='records')  # Convert the first few rows to a list of dictionaries
            
            # Return JSON response with the data
            return JSONResponse(content={"data": df_dict})
        else:
            raise HTTPException(status_code=400, detail="No valid data found.")
        
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run("main:app", port=5001, host="0.0.0.0", reload=True)