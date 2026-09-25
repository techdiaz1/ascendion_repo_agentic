from sqlalchemy import create_engine,Column,Integer,String,Numeric,Date
from sqlalchemy.orm import declarative_base,Session
from datetime import date

# PostgreSQL connection 
DATABASE_URL = "postgresql+psycopg2://postgres:12345@localhost:5432/demo_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# sales table creation 
class Sale(Base):
    __tablename__ = "sales"
    sale_id = Column(Integer,primary_key=True,autoincrement=True)
    product_name = Column(String(100))
    category = Column(String(50))
    quantity = Column(Integer)
    price_per_unit = Column(Numeric(10,2))
    sale_date = Column(Date)
# create the table 
Base.metadata.create_all(engine)
# Check if table exists (logging)
from sqlalchemy import inspect
inspector = inspect(engine)
if inspector.has_table("sales"):
    print("sales table created successfully.")
else:
    print("sales table was not created.")


# insert sample data into table sales 
with Session(engine) as session:
    session.add_all([
        Sale(
            product_name="laptop",category="electronics",quantity=1,price_per_unit=120.00,sales_date = date(2026,9,1)
        ),
        Sale(
            product_name="wireless mouse",category="electronics",quantity=3,price_per_unit=25.00,sales_date = date(2026,9,2)
        ),
        Sale(
            product_name="desk chair",category="furniture",quantity=2,price_per_unit=150.00,sales_date = date(2026,9,3)
        ),
        Sale(
            product_name="Coffee Mug",category="Kitchen",quantity=5,price_per_unit=12.00,sale_date=date(2026, 9, 4)
        ),
        Sale(
            product_name="Smartphone",category="Electronics",quantity=1,price_per_unit=800.00,sale_date=date(2026, 9, 5)
        ),
        Sale(
            product_name="Dining Table",category="Furniture",quantity=1,price_per_unit=500.00,sale_date=date(2026, 9, 6)
        )
    ])

    session.commit()

print("Sales table created and sample data inserted successfully.")



