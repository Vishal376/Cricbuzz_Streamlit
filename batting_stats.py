import requests
import sqlite3
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()

cursor.execute('''Select match_id from matches''')
match_ids=cursor.fetchall()
flat_ids=[mid[0]for mid in match_ids]

headers = {
	"x-rapidapi-key": "8009de9bedmsh9bd3306e61b428cp180c08jsn7ea8b7c26f36",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

for id in flat_ids:
   try:
     url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{id}/scard"
     response = requests.get(url, headers=headers)
     data=response.json()
     for item in data.get("scorecard", []):
       inning_no = item.get("inningsid")
    
    # batting order list
       batsmen = item.get("batsman", [])
    
       for idx, bat in enumerate(batsmen, start=1):  
         match_id = id
         player_id = bat.get("id")
         runs = bat.get("runs", 0)
         balls = bat.get("balls", 0)
         fours = bat.get("fours", 0)
         sixes = bat.get("sixes", 0)
         strike_rate = float(bat.get("strkrate", 0)) if bat.get("strkrate") else 0.0
         position = idx  

         cursor.execute('''INSERT OR IGNORE INTO batting_stats (
            match_id, player_id, runs, balls, fours, sixes, strike_rate, position,innings_no
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
         (match_id, player_id, runs, balls, fours, sixes, strike_rate, position, inning_no))
         conn.commit()
         print(idx)
   except Exception as e:
        print(f"Error in match {id}: {e}")  

conn.close()