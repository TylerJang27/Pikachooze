\COPY users(username, email, password) FROM 'data/Users.csv' WITH DELIMITER ',' NULL '' CSV
\COPY products FROM 'data/Products.csv' WITH DELIMITER ',' NULL '' CSV
\COPY purchases FROM 'data/Purchases.csv' WITH DELIMITER ',' NULL '' CSV
\COPY type FROM 'data/Types.csv' WITH DELIMITER ',' NULL '' CSV
