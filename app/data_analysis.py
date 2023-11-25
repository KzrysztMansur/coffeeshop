""" 
THIS MODULE IS FOR ALL THE DATA ANALYSIS THAT I NEED FOR THIS PROJECT WHICH IS
GETTING THE TOP 5 MOST SOLD
AND THE 3 ONES THAT ARE LEAST IN STOCK
"""
from flask_login import current_user
import pandas as pd
from flask import jsonify
import json
from app import app, db
# app/data_analysis.py
from .models import RoastedCoffee, UnroastedCoffee



def get_top_five_sold():
    # Retrieve data from the RoastedCoffee table
    roasted_coffee_data = RoastedCoffee.query.filter_by(user_id =current_user.id).all()

    # Convert data to a Pandas DataFrame
    df = pd.DataFrame([
        {'name': entry.name, 'amount_sold': entry.amount_sold} for entry in roasted_coffee_data
    ])

    # Check if the DataFrame is not empty
    if not df.empty:
        # Get the top five most sold items
        top_five = df.nlargest(5, 'amount_sold')

        # Convert the top five data back to a list of dictionaries
        top_five_data = top_five.to_dict(orient='records')

        return jsonify(data=top_five_data)
    else:
        # Handle the case when the DataFrame is empty (no data in the database)
        return []
    


from flask import jsonify

def get_least_in_stock():
    roasted_coffee_data = RoastedCoffee.query.filter_by(user_id =current_user.id).all()
    unroasted_coffee_data = UnroastedCoffee.query.filter_by(user_id =current_user.id).all()
    try:
        df_roasted = pd.DataFrame([
            {'name': entry.name, 'amount': entry.amount, 'type': 'Roasted'}
            for entry in roasted_coffee_data
        ])

        df_unroasted = pd.DataFrame([
            {'name': entry.name, 'amount': entry.amount, 'type': 'UnRoasted'}
            for entry in unroasted_coffee_data
        ])

        combined_df = pd.concat([df_roasted, df_unroasted])
        least_in_stock = combined_df.groupby('name').apply(lambda x: x.nsmallest(1, 'amount')).reset_index(drop=True)

        # Sum the amounts for each name and get the least 3 based on the total sum
        least_3_combined = combined_df.groupby('name')['amount'].sum().nsmallest(3).index
        least_3_in_stock = least_in_stock[least_in_stock['name'].isin(least_3_combined)]

        # Create a JSON response with the required format
        least_3_json = []
        for index, row in least_3_in_stock.iterrows():
            name = row['name']
            
            # Check if there are entries for the given name and type
            entries_roasted = combined_df[(combined_df['name'] == name) & (combined_df['type'] == 'Roasted')]
            entries_unroasted = combined_df[(combined_df['name'] == name) & (combined_df['type'] == 'UnRoasted')]
            
            if not entries_roasted.empty:
                amount_roasted = int(entries_roasted['amount'].values[0])  # Convert to int
            else:
                amount_roasted = 0

            if not entries_unroasted.empty:
                amount_unroasted = int(entries_unroasted['amount'].values[0])  # Convert to int
            else:
                amount_unroasted = 0

            total_sum = amount_roasted + amount_unroasted
            least_3_json.append({'name': name, 'amountRoasted': amount_roasted, 'amountUnroasted': amount_unroasted, 'totalSum': total_sum})

        return jsonify(data=least_3_json)
    except:
        return []
