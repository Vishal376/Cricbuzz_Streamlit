import requests
import time
import sqlite3

conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()
# url = "https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/scard"

headers = {
	"x-rapidapi-key": "83968a8cfamshdd6fbc840225d84p1e9229jsnfa6351a97b3a",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

cursor.execute('''SELECT match_id FROM matches''')
match_ids = cursor.fetchall()
flat_ids = [mid[0] for mid in match_ids]

for id in flat_ids:
  try:
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{id}/scard"
    response = requests.get(url, headers=headers)
    data=response.json()
    # print(data)
    for item in data.get('scorecard',[]):

      partnerships=item.get('partnership')
      for partners in partnerships.get('partnership',[]):
        match_id=id
        inning_no=item.get('inningsid')
        wicket_lost=item.get('wickets')
        striker_id=partners.get('bat1id')
        non_striker_id=partners.get('bat2id')
        runs_scored=partners.get('totalruns')
        start_pos=striker_id
        cursor.execute('''INSERT OR IGNORE INTO partnerships (
           match_id ,
           innings_no,
           striker_id ,
           non_striker_id ,
           runs_scored ,
           wickets_lost,
           start_pos )Values(?,?,?,?,?,?,?)''',(match_id,inning_no,striker_id,non_striker_id,runs_scored,wicket_lost,start_pos))
        conn.commit()
        print('happen')
        time.sleep(2)
  except Exception as e:
        print(f"Error in match {id}: {e}")

conn.close()
       