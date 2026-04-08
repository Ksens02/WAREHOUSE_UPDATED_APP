from sqlmodel import Session,select
from models import engine, Inventory

# with Session(engine) as session:
#     statement = select(Inventory)
#     records = session.exec(statement).all()
#     print(records)

# with Session(engine) as session:
#     statement = select(Inventory).where(Inventory.id == 18)
#     record = session.exec(statement).one()
#     record.quantity += 50
    
#     session.add(record)
#     session.commit()
#     session.refresh(record)

#     print("record updated")

# with Session(engine) as session:
#     newItem = Inventory(
#         name= "Bowling Ball",
#         category= "Equipment",
#         brand= "Xtreme Bowling",
#         size= "large",
#         color= "blue",
#         quantity= 50,
#         price= 75.00,
#     )

#     session.add(newItem)
#     session.commit()
#     session.refresh(newItem)

#     print("item added")

with Session(engine) as session:
    statement = select(Inventory).where(Inventory.id == 2)
    record = session.exec(statement).one()

    session.delete(record)
    session.commit()

    print("item deleted")

