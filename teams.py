# import requests
import sqlite3
import requests

conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()


headers = {
	"x-rapidapi-key": "c8e199412fmsh86cbc600130cd60p1aa609jsn62e3e9294d10",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

cursor.execute('''Select team1_id from matches''')
ids=cursor.fetchall()
fetched_ids_d=[id[0] for id in ids]
fetched_ids=list(set(fetched_ids_d))
fetched_ids.sort()
# print(fetched_ids)
cursor.execute('''Select team2_id from matches''')
ids=cursor.fetchall()
fetched_ids_d=[id[0] for id in ids]
fetched_ids2=list(set(fetched_ids_d))
fetched_ids2.sort()
# print(fetched_ids2)
final_team_ids=fetched_ids2+fetched_ids
finalids=list(set(final_team_ids))

for id in finalids:

    url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{id}/results"


    response = requests.get(url, headers=headers)

    data=response.json()
# print(data)
    team1_name = data['teamMatchesData'][0]['matchDetailsMap']['match'][0]['matchInfo']['team1']['teamName']
    cursor.execute('''Insert OR IGNORE INTO teams(team_id,team_name,country)VALUES(?,?,?)''',(id,team1_name,team1_name))
    conn.commit()

conn.close()    





















# url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/2/results"

# headers = {
# 	"x-rapidapi-key": "c8e199412fmsh86cbc600130cd60p1aa609jsn62e3e9294d10",
# 	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers)

# data=response.json()
# # print(data)
# team1_name = data['teamMatchesData'][0]['matchDetailsMap']['match'][0]['matchInfo']['team1']['teamName']
