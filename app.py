from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('forex_data.db')
    conn.row_factory = sqlite3.Row  # Allows dictionary-like access to rows
    return conn

# Calculate the date range for the given period
def get_date_range(period):
    current_date = datetime.now()
    if period == '1W':
        start_date = current_date - timedelta(days=7)
    elif period == '1M':
        start_date = current_date - timedelta(days=30)
    elif period == '3M':
        start_date = current_date - timedelta(days=90)
    elif period == '6M':
        start_date = current_date - timedelta(days=180)
    elif period == '1Y':
        start_date = current_date - timedelta(days=365)
    else:
        return None, None

    return start_date.strftime('%Y-%m-%d'), current_date.strftime('%Y-%m-%d')

# POST endpoint to fetch forex data
@app.route('/api/forex-data', methods=['POST'])
def get_forex_data():
    try:
        data = request.get_json()  
        from_currency = data.get('from')
        to_currency = data.get('to')
        period = data.get('period')

        # Validate input
        if not from_currency or not to_currency or not period:
            return jsonify({"error": "Missing 'from', 'to', or 'period' parameter"}), 400

        # Calculate the date range for the period
        from_date, to_date = get_date_range(period)

        if not from_date:
            return jsonify({"error": "Invalid period. Supported values: 1W, 1M, 3M, 6M, 1Y"}), 400

        # Table name for the currency pair
        table_name = f"exchange_rates_{from_currency}_{to_currency}"

        # Connect to the database and fetch the data
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Raise an error or return a message if the table does not exist
            return jsonify({"error": f"Table for currency pair {from_currency}/{to_currency} does not exist in the database."}), 404

        # Query to fetch data between the calculated date range
        query = f"""
        SELECT * FROM {table_name} 
        WHERE date BETWEEN ? AND ?
        """
        cursor.execute(query, (from_date, to_date))
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        result = [dict(row) for row in rows]

        # Close the connection
        conn.close()

        # Return the JSON response
        return jsonify(result), 200

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error occurred."}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
