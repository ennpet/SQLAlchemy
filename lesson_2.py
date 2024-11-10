from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import BIGINT, create_engine, DECIMAL, ForeignKey, func, INTEGER, String, TEXT, text, TIMESTAMP, URL, \
    VARCHAR
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class TableMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


user_fk = Annotated[
    int, mapped_column(BIGINT, ForeignKey("users.telegram_id", ondelete="CASCADE"))
]

int_pk = Annotated[int, mapped_column(INTEGER, primary_key=True)]

str_255 = Annotated[str, mapped_column(String(255))]


class User(Base, TimestampMixin, TableMixin):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    full_name: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    language_code: Mapped[str] = mapped_column(VARCHAR(10))
    referrer_id: Mapped[Optional[user_fk]]


class Order(Base, TimestampMixin, TableMixin):
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]


class Product(Base, TimestampMixin, TableMixin):
    product_id: Mapped[int_pk]
    title: Mapped[str_255]
    description: Mapped[Optional[str]] = mapped_column(VARCHAR(3000))
    price: Mapped[float] = mapped_column(DECIMAL(16, 4))


class OrderProduct(Base, TableMixin):
    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("products.product_id", ondelete="RESTRICT"), primary_key=True)
    quantity: Mapped[int]


if __name__ == '__main__':

    url = URL.create(
        drivername="postgresql+psycopg2",
        username="testuser",
        password="testpassword",
        host="localhost",
        port=5432,
        database="testuser"
    )
    print(url.render_as_string(hide_password=False))


    engine = create_engine(url, echo=True)
    session_pool = sessionmaker(engine)
    # with session_pool() as session:
    #     session.add(User())
    #     insert_query = text("""
    #     INSERT INTO users (telegram_id, full_name, username, language_code, referrer_id)
    #     VALUES (1, 'John Doe', 'johndoe', 'en', 2),
    #               (2, 'Jane Doe', 'janedoe', 'en', 1);
    #     """)
    #     session.execute(insert_query)
    #     session.commit()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

