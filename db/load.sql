\COPY users(username, email, password) FROM 'data/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY products FROM 'data/Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY purchases FROM 'data/Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY type FROM 'data/Types.csv' WITH DELIMITER ',' NULL '' CSV
\COPY generation FROM 'data/Generations.csv' WITH DELIMITER ',' NULL '' CSV
\COPY game FROM 'data/Games.csv' WITH DELIMITER ',' NULL '' CSV
\COPY pokemon FROM 'data/Pokemon.csv' WITH DELIMITER ',' NULL '' CSV
\COPY pokemon_base_stats FROM 'data/Stats.csv' WITH DELIMITER ',' NULL '' CSV
\copy move FROM 'data/Moves.csv' WITH DELIMITER ',' NULL '' CSV
\COPY can_learn FROM 'data/Learn.csv' WITH DELIMITER ',' NULL '' CSV
