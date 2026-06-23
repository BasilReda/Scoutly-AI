-- ============================================================
-- Football Player Database — SQLite Seed Data (55 Players)
-- Positions: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
-- Run via:  python data/init_db.py
-- ============================================================

CREATE TABLE IF NOT EXISTS players (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name               TEXT    NOT NULL,
    nationality        TEXT,
    position           TEXT,
    age                INTEGER,
    club               TEXT,
    wage_eur           INTEGER,
    value_eur          INTEGER,
    overall_rating     INTEGER,
    potential          INTEGER,
    goals_per_season   REAL,
    assists_per_season REAL,
    pass_accuracy      REAL,
    dribble_success    REAL,
    aerial_duels_won   REAL,
    sprint_speed       INTEGER,
    stamina            INTEGER,
    defending          REAL,
    attacking          REAL,
    physicality        REAL,
    seasons_data       TEXT    -- JSON stored as text
);

DELETE FROM players;

INSERT INTO players (name, nationality, position, age, club, wage_eur, value_eur, overall_rating, potential, goals_per_season, assists_per_season, pass_accuracy, dribble_success, aerial_duels_won, sprint_speed, stamina, defending, attacking, physicality, seasons_data) VALUES

-- ═══════════════════════════════════════════
-- GOALKEEPERS (5)
-- ═══════════════════════════════════════════
('Marco Lindelöf',   'German',    'GK', 29, 'Bayer Leverkusen',     35000, 22000000, 85, 86, 0.2, 0.1, 78.0, 35.0, 72.0, 52, 72, 78.0, 20.0, 76.0, '[{"season":"2021/22","goals":0,"assists":0,"apps":32,"clean_sheets":14},{"season":"2022/23","goals":0,"assists":1,"apps":35,"clean_sheets":17},{"season":"2023/24","goals":0,"assists":0,"apps":34,"clean_sheets":15}]'),
('Pierre Beaumont',  'French',    'GK', 27, 'Olympique Lyon',       25000, 15000000, 82, 85, 0.1, 0.0, 74.0, 30.0, 68.0, 50, 68, 75.0, 18.0, 72.0, '[{"season":"2021/22","goals":0,"assists":0,"apps":30,"clean_sheets":10},{"season":"2022/23","goals":0,"assists":0,"apps":33,"clean_sheets":12},{"season":"2023/24","goals":0,"assists":1,"apps":35,"clean_sheets":14}]'),
('Jan Kowalski',     'Polish',    'GK', 31, 'Lech Poznan',          20000,  8000000, 78, 78, 0.0, 0.0, 70.0, 28.0, 65.0, 48, 65, 72.0, 16.0, 70.0, '[{"season":"2021/22","goals":0,"assists":0,"apps":28,"clean_sheets":9},{"season":"2022/23","goals":0,"assists":0,"apps":32,"clean_sheets":11},{"season":"2023/24","goals":0,"assists":0,"apps":30,"clean_sheets":10}]'),
('Eduardo Pires',    'Brazilian', 'GK', 26, 'Athletico Paranaense', 18000,  9000000, 79, 84, 0.1, 0.0, 72.0, 32.0, 66.0, 55, 70, 74.0, 17.0, 71.0, '[{"season":"2021/22","goals":0,"assists":0,"apps":27,"clean_sheets":8},{"season":"2022/23","goals":0,"assists":0,"apps":30,"clean_sheets":11},{"season":"2023/24","goals":0,"assists":0,"apps":33,"clean_sheets":13}]'),
('Sebastián Molina', 'Spanish',   'GK', 28, 'Valencia CF',          30000, 18000000, 83, 83, 0.0, 0.0, 76.0, 33.0, 70.0, 51, 71, 77.0, 19.0, 74.0, '[{"season":"2021/22","goals":0,"assists":0,"apps":33,"clean_sheets":13},{"season":"2022/23","goals":0,"assists":0,"apps":35,"clean_sheets":15},{"season":"2023/24","goals":0,"assists":1,"apps":36,"clean_sheets":16}]'),

-- ═══════════════════════════════════════════
-- CENTRE-BACKS (8)
-- ═══════════════════════════════════════════
('Alessandro Ricci',     'Italian',    'CB', 30, 'AC Milan',              55000, 38000000, 88, 88, 2.1, 1.5, 82.0, 45.0, 82.0, 64, 78, 89.0, 52.0, 85.0, '[{"season":"2021/22","goals":2,"assists":1,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":2,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":1,"assists":1,"apps":33,"clean_sheets":0}]'),
('Thomas Blanchard',     'French',     'CB', 25, 'Paris Saint-Germain',   65000, 52000000, 86, 91, 1.8, 1.2, 85.0, 50.0, 80.0, 70, 80, 87.0, 55.0, 82.0, '[{"season":"2021/22","goals":1,"assists":1,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":1,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":2,"apps":35,"clean_sheets":0}]'),
('Vincent Van den Berg', 'Dutch',      'CB', 29, 'Ajax Amsterdam',        48000, 30000000, 84, 84, 2.5, 1.0, 80.0, 42.0, 79.0, 62, 76, 86.0, 50.0, 83.0, '[{"season":"2021/22","goals":2,"assists":0,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":1,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":1,"apps":31,"clean_sheets":0}]'),
('Bruno Almeida',        'Portuguese', 'CB', 27, 'Sporting CP',           42000, 28000000, 83, 86, 1.5, 1.8, 83.0, 48.0, 77.0, 68, 79, 84.0, 53.0, 80.0, '[{"season":"2021/22","goals":1,"assists":2,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":1,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":1,"assists":2,"apps":35,"clean_sheets":0}]'),
('Jack Henderson',       'English',    'CB', 26, 'Chelsea FC',            70000, 55000000, 85, 88, 2.0, 1.0, 81.0, 44.0, 83.0, 65, 80, 88.0, 51.0, 84.0, '[{"season":"2021/22","goals":1,"assists":1,"apps":29,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":0,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":1,"apps":35,"clean_sheets":0}]'),
('Carlos Vidal',         'Spanish',    'CB', 31, 'Atlético Madrid',       60000, 32000000, 87, 87, 3.0, 1.2, 84.0, 46.0, 84.0, 60, 75, 90.0, 52.0, 86.0, '[{"season":"2021/22","goals":3,"assists":1,"apps":33,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":2,"apps":30,"clean_sheets":0},{"season":"2023/24","goals":4,"assists":1,"apps":32,"clean_sheets":0}]'),
('Klaus Hoffmann',       'German',     'CB', 28, 'FC Bayern Munich',      85000, 62000000, 89, 89, 2.8, 2.0, 86.0, 52.0, 85.0, 66, 81, 91.0, 56.0, 87.0, '[{"season":"2021/22","goals":2,"assists":2,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":2,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":2,"apps":35,"clean_sheets":0}]'),
('Santiago Rojas',       'Argentine',  'CB', 24, 'River Plate',           22000, 14000000, 80, 87, 1.2, 0.8, 78.0, 40.0, 76.0, 72, 78, 82.0, 48.0, 78.0, '[{"season":"2021/22","goals":1,"assists":0,"apps":25,"clean_sheets":0},{"season":"2022/23","goals":1,"assists":1,"apps":30,"clean_sheets":0},{"season":"2023/24","goals":1,"assists":1,"apps":33,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- LEFT-BACKS (4)
-- ═══════════════════════════════════════════
('Roberto Santos',  'Brazilian', 'LB', 27, 'Flamengo',          30000, 20000000, 83, 84, 3.5, 5.2, 80.0, 65.0, 62.0, 80, 83, 76.0, 72.0, 74.0, '[{"season":"2021/22","goals":3,"assists":5,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":4,"assists":6,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":5,"apps":34,"clean_sheets":0}]'),
('Marcos Iglesias', 'Spanish',   'LB', 26, 'Real Sociedad',     38000, 26000000, 82, 84, 2.8, 4.5, 82.0, 62.0, 58.0, 78, 81, 75.0, 70.0, 72.0, '[{"season":"2021/22","goals":2,"assists":4,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":5,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":4,"apps":34,"clean_sheets":0}]'),
('Liam Watson',     'English',   'LB', 28, 'Manchester United', 55000, 38000000, 81, 81, 2.0, 3.8, 78.0, 60.0, 55.0, 76, 79, 74.0, 68.0, 71.0, '[{"season":"2021/22","goals":2,"assists":3,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":1,"assists":4,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":4,"apps":33,"clean_sheets":0}]'),
('Théo Dumont',     'French',    'LB', 22, 'AS Monaco',         20000, 12000000, 78, 87, 1.5, 3.2, 76.0, 58.0, 52.0, 82, 80, 72.0, 65.0, 68.0, '[{"season":"2021/22","goals":1,"assists":2,"apps":22,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":3,"apps":28,"clean_sheets":0},{"season":"2023/24","goals":1,"assists":4,"apps":32,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- RIGHT-BACKS (4)
-- ═══════════════════════════════════════════
('Felix Braun',     'German',     'RB', 25, 'RB Leipzig',  42000, 30000000, 83, 87, 2.5, 5.5, 81.0, 63.0, 60.0, 82, 82, 75.0, 71.0, 73.0, '[{"season":"2021/22","goals":2,"assists":5,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":6,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":5,"apps":35,"clean_sheets":0}]'),
('Ryan Cooper',     'English',    'RB', 29, 'Liverpool FC', 62000, 42000000, 84, 84, 2.2, 5.0, 82.0, 61.0, 62.0, 79, 80, 77.0, 70.0, 75.0, '[{"season":"2021/22","goals":2,"assists":5,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":5,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":5,"apps":35,"clean_sheets":0}]'),
('Gonçalo Pereira', 'Portuguese', 'RB', 24, 'SL Benfica',   28000, 18000000, 80, 86, 1.8, 4.2, 78.0, 58.0, 57.0, 80, 78, 73.0, 67.0, 70.0, '[{"season":"2021/22","goals":1,"assists":3,"apps":25,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":4,"apps":30,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":5,"apps":33,"clean_sheets":0}]'),
('Lucas Ferreira',  'Brazilian',  'RB', 26, 'SE Palmeiras', 25000, 14000000, 81, 83, 2.0, 4.8, 79.0, 62.0, 58.0, 84, 81, 74.0, 69.0, 72.0, '[{"season":"2021/22","goals":2,"assists":4,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":5,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":5,"apps":33,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- DEFENSIVE MIDFIELDERS (4)
-- ═══════════════════════════════════════════
('Antoine Mercier', 'French',     'CDM', 28, 'OGC Nice',            48000, 32000000, 84, 84, 3.2, 4.5, 86.0, 60.0, 72.0, 70, 85, 82.0, 62.0, 80.0, '[{"season":"2021/22","goals":3,"assists":4,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":3,"assists":5,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":4,"apps":35,"clean_sheets":0}]'),
('Sergio Navarro',  'Spanish',    'CDM', 30, 'Sevilla FC',           52000, 28000000, 85, 85, 2.8, 4.0, 87.0, 58.0, 75.0, 67, 83, 84.0, 60.0, 82.0, '[{"season":"2021/22","goals":3,"assists":4,"apps":33,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":5,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":3,"assists":3,"apps":34,"clean_sheets":0}]'),
('Mamadou Diallo',  'Senegalese', 'CDM', 27, 'Stade Rennais',        32000, 22000000, 81, 83, 2.0, 3.8, 83.0, 55.0, 78.0, 72, 87, 81.0, 58.0, 84.0, '[{"season":"2021/22","goals":2,"assists":3,"apps":29,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":4,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":2,"assists":4,"apps":34,"clean_sheets":0}]'),
('Tim Richter',     'German',     'CDM', 29, 'Borussia Dortmund',    55000, 35000000, 83, 83, 3.0, 5.0, 85.0, 57.0, 74.0, 68, 84, 83.0, 61.0, 81.0, '[{"season":"2021/22","goals":3,"assists":5,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":2,"assists":5,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":4,"assists":5,"apps":35,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- CENTRAL MIDFIELDERS (6)
-- ═══════════════════════════════════════════
('David Torres',   'Spanish',   'CM', 26, 'FC Barcelona', 80000, 75000000, 88, 91, 8.5,  9.2, 91.0, 75.0, 65.0, 78, 88, 62.0, 82.0, 72.0, '[{"season":"2021/22","goals":7,"assists":9,"apps":33,"clean_sheets":0},{"season":"2022/23","goals":9,"assists":9,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":9,"assists":10,"apps":36,"clean_sheets":0}]'),
('James Mitchell', 'English',   'CM', 28, 'Arsenal FC',   75000, 68000000, 86, 86, 7.2,  8.5, 89.0, 72.0, 62.0, 76, 86, 60.0, 80.0, 70.0, '[{"season":"2021/22","goals":6,"assists":8,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":8,"assists":8,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":7,"assists":9,"apps":35,"clean_sheets":0}]'),
('Stefan Müller',  'German',    'CM', 25, 'Bayer Leverkusen', 58000, 52000000, 84, 89, 6.5, 7.8, 88.0, 70.0, 60.0, 75, 85, 58.0, 78.0, 68.0, '[{"season":"2021/22","goals":5,"assists":7,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":7,"assists":8,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":7,"assists":8,"apps":35,"clean_sheets":0}]'),
('Luka Petrov',    'Croatian',  'CM', 30, 'Dinamo Zagreb', 35000, 20000000, 82, 82, 6.0, 7.0, 86.0, 68.0, 58.0, 72, 82, 56.0, 75.0, 66.0, '[{"season":"2021/22","goals":5,"assists":7,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":6,"assists":7,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":7,"assists":7,"apps":35,"clean_sheets":0}]'),
('Kevin Desmet',   'Belgian',   'CM', 27, 'Club Brugge',   30000, 18000000, 81, 83, 5.5, 6.5, 85.0, 66.0, 56.0, 73, 83, 54.0, 73.0, 65.0, '[{"season":"2021/22","goals":5,"assists":6,"apps":29,"clean_sheets":0},{"season":"2022/23","goals":5,"assists":7,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":6,"assists":6,"apps":34,"clean_sheets":0}]'),
('Gabriel Mendes', 'Brazilian', 'CM', 24, 'Santos FC',     28000, 16000000, 80, 87, 5.0, 6.0, 83.0, 64.0, 54.0, 76, 82, 52.0, 71.0, 63.0, '[{"season":"2021/22","goals":4,"assists":5,"apps":26,"clean_sheets":0},{"season":"2022/23","goals":5,"assists":6,"apps":30,"clean_sheets":0},{"season":"2023/24","goals":6,"assists":7,"apps":33,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- ATTACKING MIDFIELDERS (4)
-- ═══════════════════════════════════════════
('Kai Becker',      'German',    'CAM', 23, 'RB Leipzig',           65000, 58000000, 85, 92, 12.0, 10.5, 87.0, 80.0, 55.0, 82, 80, 42.0, 88.0, 65.0, '[{"season":"2021/22","goals":10,"assists":10,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":12,"assists":11,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":14,"assists":10,"apps":35,"clean_sheets":0}]'),
('Diogo Ferreira',  'Portuguese','CAM', 25, 'FC Porto',             55000, 48000000, 84, 87, 11.0,  9.8, 86.0, 78.0, 52.0, 80, 79, 40.0, 86.0, 63.0, '[{"season":"2021/22","goals":9,"assists":9,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":11,"assists":10,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":13,"assists":10,"apps":35,"clean_sheets":0}]'),
('Nicolás Herrera', 'Argentine', 'CAM', 26, 'Racing Club',          32000, 22000000, 82, 85,  9.5,  8.5, 83.0, 76.0, 50.0, 79, 77, 38.0, 83.0, 60.0, '[{"season":"2021/22","goals":8,"assists":8,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":10,"assists":8,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":11,"assists":9,"apps":34,"clean_sheets":0}]'),
('Mathieu Girard',  'French',    'CAM', 27, 'Olympique Marseille',  68000, 55000000, 86, 86, 13.0, 11.0, 88.0, 81.0, 54.0, 81, 81, 43.0, 87.0, 64.0, '[{"season":"2021/22","goals":11,"assists":10,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":13,"assists":11,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":15,"assists":11,"apps":36,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- LEFT WINGERS (5)
-- ═══════════════════════════════════════════
('Caio Rodrigues',  'Brazilian', 'LW', 22, 'Fluminense FC',  28000, 20000000, 82, 90, 10.5, 8.2, 78.0, 82.0, 48.0, 91, 80, 32.0, 85.0, 60.0, '[{"season":"2021/22","goals":9,"assists":8,"apps":27,"clean_sheets":0},{"season":"2022/23","goals":10,"assists":8,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":12,"assists":8,"apps":34,"clean_sheets":0}]'),
('Clément Moreau',  'French',    'LW', 25, 'Olympique Lyon', 60000, 55000000, 85, 87, 14.0, 9.5, 80.0, 84.0, 50.0, 90, 82, 34.0, 87.0, 62.0, '[{"season":"2021/22","goals":12,"assists":9,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":14,"assists":9,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":16,"assists":10,"apps":35,"clean_sheets":0}]'),
('João Silva',      'Portuguese','LW', 26, 'Sporting CP',    55000, 50000000, 84, 85, 13.0,10.0, 79.0, 83.0, 49.0, 88, 81, 33.0, 86.0, 61.0, '[{"season":"2021/22","goals":11,"assists":10,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":13,"assists":10,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":15,"assists":10,"apps":35,"clean_sheets":0}]'),
('Adrián Ruiz',     'Spanish',   'LW', 28, 'Real Betis',     45000, 35000000, 83, 83, 11.5, 8.8, 79.0, 81.0, 47.0, 86, 79, 32.0, 84.0, 59.0, '[{"season":"2021/22","goals":10,"assists":8,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":12,"assists":9,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":12,"assists":9,"apps":34,"clean_sheets":0}]'),
('Marcus Green',    'English',   'LW', 23, 'Leeds United',   25000, 15000000, 79, 86,  8.5, 7.2, 75.0, 79.0, 45.0, 93, 78, 30.0, 81.0, 57.0, '[{"season":"2021/22","goals":7,"assists":6,"apps":24,"clean_sheets":0},{"season":"2022/23","goals":9,"assists":7,"apps":30,"clean_sheets":0},{"season":"2023/24","goals":9,"assists":8,"apps":33,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- RIGHT WINGERS (5)
-- ═══════════════════════════════════════════
('Javier Ramos',    'Argentine', 'RW', 24, 'San Lorenzo',         22000, 16000000, 81, 88, 11.0, 8.5, 76.0, 83.0, 46.0, 92, 79, 31.0, 84.0, 58.0, '[{"season":"2021/22","goals":9,"assists":8,"apps":27,"clean_sheets":0},{"season":"2022/23","goals":11,"assists":8,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":13,"assists":9,"apps":34,"clean_sheets":0}]'),
('Rafael Costa',    'Portuguese','RW', 27, 'SL Benfica',           52000, 48000000, 85, 86, 14.5,10.2, 78.0, 85.0, 48.0, 89, 82, 33.0, 88.0, 61.0, '[{"season":"2021/22","goals":12,"assists":10,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":15,"assists":10,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":16,"assists":10,"apps":35,"clean_sheets":0}]'),
('Alejandro Díaz',  'Spanish',   'RW', 25, 'Real Madrid CF',       95000, 90000000, 88, 90, 16.0,11.5, 80.0, 88.0, 50.0, 91, 83, 35.0, 91.0, 63.0, '[{"season":"2021/22","goals":13,"assists":11,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":16,"assists":11,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":19,"assists":12,"apps":36,"clean_sheets":0}]'),
('Baptiste Renard', 'French',    'RW', 26, 'Paris Saint-Germain',  88000, 82000000, 87, 88, 15.0,10.8, 79.0, 87.0, 49.0, 90, 82, 34.0, 90.0, 62.0, '[{"season":"2021/22","goals":12,"assists":10,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":15,"assists":11,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":18,"assists":11,"apps":35,"clean_sheets":0}]'),
('Enzo Carvalho',   'Brazilian', 'RW', 21, 'Grêmio FBPA',          20000, 12000000, 78, 90,  9.0, 7.5, 74.0, 80.0, 44.0, 93, 77, 29.0, 80.0, 56.0, '[{"season":"2021/22","goals":7,"assists":6,"apps":22,"clean_sheets":0},{"season":"2022/23","goals":9,"assists":7,"apps":28,"clean_sheets":0},{"season":"2023/24","goals":11,"assists":8,"apps":33,"clean_sheets":0}]'),

-- ═══════════════════════════════════════════
-- STRIKERS (10)
-- ═══════════════════════════════════════════
('Harry Powell',    'English',   'ST', 27, 'Tottenham Hotspur', 85000, 80000000, 87, 87, 22.0, 7.5, 72.0, 72.0, 75.0, 84, 78, 38.0, 90.0, 82.0, '[{"season":"2021/22","goals":20,"assists":7,"apps":33,"clean_sheets":0},{"season":"2022/23","goals":22,"assists":7,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":24,"assists":8,"apps":36,"clean_sheets":0}]'),
('Lucas Martin',    'French',    'ST', 26, 'AS Monaco',          78000, 72000000, 86, 88, 21.0, 8.0, 71.0, 73.0, 72.0, 86, 79, 37.0, 89.0, 80.0, '[{"season":"2021/22","goals":18,"assists":8,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":21,"assists":8,"apps":35,"clean_sheets":0},{"season":"2023/24","goals":24,"assists":8,"apps":35,"clean_sheets":0}]'),
('Robert Kozlowski','Polish',    'ST', 29, 'Legia Warsaw',        35000, 22000000, 82, 82, 17.0, 5.5, 68.0, 65.0, 78.0, 78, 74, 36.0, 84.0, 83.0, '[{"season":"2021/22","goals":15,"assists":5,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":17,"assists":6,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":19,"assists":5,"apps":34,"clean_sheets":0}]'),
('Lars Andersen',   'Norwegian', 'ST', 23, 'Molde FK',            25000, 18000000, 80, 88, 16.0, 4.5, 66.0, 62.0, 74.0, 83, 75, 34.0, 82.0, 80.0, '[{"season":"2021/22","goals":13,"assists":4,"apps":27,"clean_sheets":0},{"season":"2022/23","goals":16,"assists":4,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":19,"assists":5,"apps":33,"clean_sheets":0}]'),
('Marco Ferrara',   'Italian',   'ST', 30, 'AS Roma',             72000, 52000000, 85, 85, 20.0, 6.5, 70.0, 70.0, 76.0, 80, 76, 37.0, 88.0, 82.0, '[{"season":"2021/22","goals":18,"assists":6,"apps":32,"clean_sheets":0},{"season":"2022/23","goals":20,"assists":7,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":22,"assists":6,"apps":35,"clean_sheets":0}]'),
('Diego Acosta',    'Argentine', 'ST', 25, 'Boca Juniors',        30000, 24000000, 83, 87, 18.5, 6.0, 69.0, 68.0, 72.0, 82, 77, 35.0, 86.0, 79.0, '[{"season":"2021/22","goals":16,"assists":5,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":19,"assists":6,"apps":33,"clean_sheets":0},{"season":"2023/24","goals":21,"assists":7,"apps":34,"clean_sheets":0}]'),
('Felipe Nunes',    'Brazilian', 'ST', 24, 'SC Corinthians',      28000, 20000000, 81, 86, 16.5, 5.8, 67.0, 66.0, 70.0, 85, 76, 33.0, 84.0, 78.0, '[{"season":"2021/22","goals":14,"assists":5,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":17,"assists":6,"apps":31,"clean_sheets":0},{"season":"2023/24","goals":18,"assists":6,"apps":33,"clean_sheets":0}]'),
('Pablo Morales',   'Spanish',   'ST', 28, 'Villarreal CF',       68000, 55000000, 84, 84, 19.5, 7.0, 71.0, 70.0, 73.0, 81, 78, 36.0, 87.0, 81.0, '[{"season":"2021/22","goals":17,"assists":7,"apps":31,"clean_sheets":0},{"season":"2022/23","goals":20,"assists":7,"apps":34,"clean_sheets":0},{"season":"2023/24","goals":21,"assists":7,"apps":35,"clean_sheets":0}]'),
('Pieter de Vries', 'Dutch',     'ST', 31, 'PSV Eindhoven',       65000, 42000000, 83, 83, 18.0, 5.5, 70.0, 68.0, 77.0, 79, 73, 36.0, 86.0, 83.0, '[{"season":"2021/22","goals":16,"assists":5,"apps":30,"clean_sheets":0},{"season":"2022/23","goals":18,"assists":5,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":20,"assists":6,"apps":33,"clean_sheets":0}]'),
('Adrien Guillaume','Belgian',   'ST', 26, 'RSC Anderlecht',      38000, 28000000, 80, 84, 14.5, 5.2, 68.0, 64.0, 68.0, 83, 77, 32.0, 83.0, 76.0, '[{"season":"2021/22","goals":12,"assists":5,"apps":28,"clean_sheets":0},{"season":"2022/23","goals":15,"assists":5,"apps":32,"clean_sheets":0},{"season":"2023/24","goals":17,"assists":5,"apps":34,"clean_sheets":0}]');

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_players_position      ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_wage          ON players(wage_eur);
CREATE INDEX IF NOT EXISTS idx_players_rating        ON players(overall_rating);
CREATE INDEX IF NOT EXISTS idx_players_position_wage ON players(position, wage_eur);
