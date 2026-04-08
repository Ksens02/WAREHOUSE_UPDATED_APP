from sqlmodel import Session, select
from models import Inventory, engine

# Update example
with Session(engine) as session:
    statement = select(Inventory).where(Inventory.id == 18)
    basketball = session.exec(statement).one()

    print(basketball)

    basketball.quantity += 50

    session.add(basketball)
    session.commit()
    session.refresh(basketball)

    print(basketball)

# Create example
with Session(engine) as session:
    new_item = Inventory(
        name="Speed Jump Rope",
        category="Equipment",
        brand="Rogue",
        size=None,
        color="Red",
        quantity=75,
        price=24.99,
    )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    print(new_item)

# Delete example
with Session(engine) as session:
    statement = select(Inventory).where(Inventory.id == 1)
    item = session.exec(statement).one()

    print(item)

    session.delete(item)
    session.commit()

    print("Item deleted.")