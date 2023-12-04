import pandas as pd
import sqlite3

def initialize_database():
    conn = sqlite3.connect('store_data.db')

    # Read CSV files with specific data types
    store_status_df = pd.read_csv('static/store_status.csv', dtype={'store_id': str})
    store_status_df['timestamp_utc'] = pd.to_datetime(store_status_df['timestamp_utc'])

    menu_hours_df = pd.read_csv('static/menu_hours.csv', dtype={'store_id': str})
    # Specify the format for time columns
    menu_hours_df['start_time_local'] = pd.to_datetime(menu_hours_df['start_time_local'], format='%H:%M:%S').dt.time
    menu_hours_df['end_time_local'] = pd.to_datetime(menu_hours_df['end_time_local'], format='%H:%M:%S').dt.time

    timezone_df = pd.read_csv('static/store_timezone.csv', dtype={'store_id': str})

    # Create tables and import data into SQLite
    store_status_df.to_sql('store_status', conn, if_exists='replace', index=False)
    menu_hours_df.to_sql('menu_hours', conn, if_exists='replace', index=False)
    timezone_df.to_sql('timezones', conn, if_exists='replace', index=False)

    conn.close()

initialize_database()
