import requests
import pandas as pd
import sqlite3

url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/international"

headers = {
	"x-rapidapi-key": "6796a80ac5msh4a746c443e4b49ap189a1fjsnc9180bf957e4",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

data=response.json()
# print(data)
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()
for block in data.get("seriesMapProto", []):
    for series in block.get("series", []):
        series_id = series.get("id")
        name = series.get("name")
        
        # Convert millis → date
        start_date = pd.to_datetime(int(series.get("startDt")), unit="ms").strftime("%Y-%m-%d") if series.get("startDt") else None
        end_date =pd.to_datetime(int(series.get("endDt")),unit="ms").strftime("%Y-%m-%d") if series.get("endDt") else None
        
        cursor.execute("""
    INSERT INTO series_id_name (series_id, series_name, series_start, series_end)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(series_id) DO UPDATE SET 
        series_name=excluded.series_name,
        series_start=excluded.series_start,
        series_end=excluded.series_end
""", (series_id, name, start_date, end_date))

conn.commit()
conn.close()