USE db-nfc-game;

CREATE TABLE IF NOT EXISTS Card (
    id_card INT AUTO_INCREMENT PRIMARY KEY,
    title_card VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    detail_card TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    tick_card TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    path_image_card VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    count_scan_card INT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS BoardGame (
    id_boardgame INT AUTO_INCREMENT PRIMARY KEY,
    title_game VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    detail_game TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    path_image_boardgame VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    path_youtube VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    player_recommend_start INT,
    player_recommend_end INT,
    age_recommend INT,
    time_playing INT,
    recommend BOOLEAN,
    type_game VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    count_scan_boardgame INT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Report (
    id_report INT AUTO_INCREMENT PRIMARY KEY,
    id_boardgame INT,
    FOREIGN KEY (id_boardgame) REFERENCES BoardGame(id_boardgame),
    count_scan_card INT,
    count_scan_boardgame INT,
    date_report DATETIME DEFAULT CURRENT_TIMESTAMP,
    checktypes VARCHAR(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    detail_report TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    rating INT,
    name_report VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    contact VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS Connect_BoardGame_Card (
    id_total_boardgame INT AUTO_INCREMENT PRIMARY KEY,
    id_card INT,
    FOREIGN KEY (id_card) REFERENCES Card(id_card),
    id_boardgame INT,
    FOREIGN KEY (id_boardgame) REFERENCES BoardGame(id_boardgame)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
