import sqlite3
import requests
import time
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()

cursor.execute('''Select venue_id from matches''')
ids=cursor.fetchall()
fetched_ids_d=[id[0] for id in ids]
fetched_ids=list(set(fetched_ids_d))

# url = "https://cricbuzz-cricket.p.rapidapi.com/venues/v1/45"

headers = {
	"x-rapidapi-key": "c8e199412fmsh86cbc600130cd60p1aa609jsn62e3e9294d10",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


# l=[458]

for id in fetched_ids:
    if not id:  # skip None or 0
        continue
    try:
     url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{id}"
     response = requests.get(url, headers=headers)
     data=response.json()
     time.sleep(1)
     venue_id=id
     name=data.get('ground')or ""
     city=data.get('city')or""
     country=data.get('country')or""
     capacity=data.get('capacity')or None
     cursor.execute('''Insert OR IGNORE INTO venues(venue_id,name,city,country,capacity)VALUES(?,?,?,?,?)''',
                   (venue_id,name,city,country,capacity))

     print(venue_id,name,city,country,capacity)
     conn.commit()
    except Exception as e:
        print(f"Error in match {id}: {e}")  

conn.close()  




