from sqlalchemy.orm import Session
from app.models.purchase import Purchase

print("About to print purchases:")
session = Session()
# print(session.get_bind().table_names())
# print(session)
print(session.query(Purchase).all())