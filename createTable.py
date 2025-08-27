import sqlite3
conn=sqlite3.connect('cricbuzz.db')
cursor=conn.cursor()
cursor.execute('''CREATE TABLE players (
    player_id      SERIAL PRIMARY KEY,
    full_name      VARCHAR(100),
    country        VARCHAR(50),
    playing_role   VARCHAR(50),   -- Batsman, Bowler, All-rounder, Wicket-keeper
    batting_style  VARCHAR(50),
    bowling_style  VARCHAR(50)
);
''')
cursor.execute('''CREATE TABLE teams (
    team_id    SERIAL PRIMARY KEY,
    team_name  VARCHAR(100),
    country    VARCHAR(50)
);''')

cursor.execute('''CREATE TABLE venues (
    venue_id   SERIAL PRIMARY KEY,
    name       VARCHAR(100),
    city       VARCHAR(100),
    country    VARCHAR(100),
    capacity   INT
);
''')

cursor.execute('''CREATE TABLE series_id_name (
    series_id     SERIAL PRIMARY KEY,
    series_name   VARCHAR(200),
    series_start  DATE,
    series_end    DATE    )             ''')

cursor.execute('''CREATE TABLE seriesmatches (
    series_id     SERIAL PRIMARY KEY,
    series_name   VARCHAR(200),
    host_country  VARCHAR(100),
    match_type    VARCHAR(20),   -- Test, ODI, T20I
    start_date    DATE,
    total_matches INT
);''')

cursor.execute('''CREATE TABLE matches (
    match_id        SERIAL PRIMARY KEY,
    series_id       INT REFERENCES series(series_id),
    description     VARCHAR(200),
    team1_id        INT REFERENCES teams(team_id),
    team2_id        INT REFERENCES teams(team_id),
    venue_id        INT REFERENCES venues(venue_id),
    match_date      DATE,
    toss_winner_id  INT REFERENCES teams(team_id),
    toss_decision   VARCHAR(10),   -- bat/bowl
    winner_id       INT REFERENCES teams(team_id),
    victory_margin  INT,
    victory_type    VARCHAR(20)    -- runs/wickets
);''')

cursor.execute('''CREATE TABLE batting_stats (
    match_id     INT REFERENCES matches(match_id),
    player_id    INT REFERENCES players(player_id),
    runs         INT,
    balls        INT,
    fours        INT,
    sixes        INT,
    strike_rate  FLOAT,
    position     INT,
    PRIMARY KEY (match_id, player_id)
);''')

cursor.execute('''CREATE TABLE bowling_stats (
    match_id        INT REFERENCES matches(match_id),
    player_id       INT REFERENCES players(player_id),
    overs           FLOAT,
    maidens         INT,
    runs_conceded   INT,
    wickets         INT,
    economy         FLOAT,
    PRIMARY KEY (match_id, player_id)
);
''')
cursor.execute('''CREATE TABLE fielding_stats (
    match_id   INT REFERENCES matches(match_id),
    player_id  INT REFERENCES players(player_id),
    catches    INT,
    stumpings  INT,
    PRIMARY KEY (match_id, player_id)
);''')

cursor.execute('''CREATE TABLE partnerships (
    match_id      INT REFERENCES matches(match_id),
    innings_no    INT,
    striker_id    INT REFERENCES players(player_id),
    non_striker_id INT REFERENCES players(player_id),
    runs_scored   INT,
    wickets_lost  INT,
    start_pos     INT, -- e.g., 1 for opening partnership
    PRIMARY KEY (match_id, innings_no, striker_id, non_striker_id)
);''')

conn.commit()
conn.close()