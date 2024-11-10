import random

from faker import Faker
from sqlalchemy import create_engine, delete, select, URL
from sqlalchemy.dialects.postgresql import insert

from sqlalchemy.orm import sessionmaker
from environs import Env
from sqlalchemy.sql.operators import or_

from lesson_2 import Order, OrderProduct, Product, User

env = Env()
env.read_env(".env")


class Repo:
    def __init__(self, session):
        self.session = session

    def add_user(
        self,
        telegram_id: int,
        full_name: str,
        language_code: str,
        user_name: str = None,
        referrer_id: str = None,
    ) -> User:
        stmt = select(User).from_statement(
            insert(User)
            .values(
                telegram_id=telegram_id,
                user_name=user_name,
                full_name=full_name,
                language_code=language_code,
                referrer_id=referrer_id,
            )
            .returning(User)
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_=dict(
                    user_name=user_name,
                    full_name=full_name,
                ),
            )
        )
        print(stmt)
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def get_user_by_id(self, telegram_id: int) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def get_all_users(self):
        stmt = (
            select(User)
            .where(
                or_(User.language_code == "en", User.language_code == "uk"),
                User.user_name.ilike("%john%"),
            )
            .order_by(User.created_at)
            .limit(10)
            .group_by(User.telegram_id)
            .having(User.telegram_id > 0)
        )
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get_user_language(self, telegram_id: int) -> str:
        stmt = select(User.language_code).where(User.telegram_id == telegram_id)
        result = self.session.execute(stmt)
        return result.scalar()

    def add_order(self, user_id: int) -> Order:
        stmt = select(Order).from_statement(
            insert(Order).values(user_id=user_id).returning(Order)
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def add_product(self, title: str, description: str, price: float) -> Product:
        stmt = select(Product).from_statement(
            insert(Product)
            .values(title=title, description=description, price=price)
            .returning(Product)
        )
        result = self.session.scalars(stmt)
        self.session.commit()
        return result.first()

    def add_product_to_order(self, order_id: int, product_id: int, quantity: int):
        stmt = (
            insert(OrderProduct)
            .values(order_id=order_id, product_id=product_id, quantity=quantity)
        )
        self.session.execute(stmt)
        self.session.commit()


def seed_fake_data(repo: Repo):
    Faker.seed(0)
    fake = Faker()
    users = []
    orders = []
    products = []

    for _ in range(10):
        referrer_id = None if not users else users[-1].telegram_id
        user = repo.add_user(
            telegram_id=fake.pyint(),
            full_name=fake.name(),
            language_code=fake.language_code(),
            user_name=fake.user_name(),
            referrer_id=referrer_id,
        )
        users.append(user)

    for _ in range(10):
        order = repo.add_order(user_id=random.choice(users).telegram_id)
        orders.append(order)

    for _ in range(10):
        product = repo.add_product(
            title=fake.word(), description=fake.sentence(), price=fake.pyfloat(min_value=0, max_value=1000)
        )
        products.append(product)

    for order in orders:
        for _ in range(3):
            repo.add_product_to_order(
                order_id=order.order_id, product_id=random.choice(products).product_id, quantity=fake.pyint()
            )


if __name__ == "__main__":
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=env.str("POSTGRES_USER"),
        password=env.str("POSTGRES_PASSWORD"),
        host=env.str("DATABASE_HOST"),
        port=5432,
        database=env.str("POSTGRES_DB"),
    )

    engine = create_engine(url, echo=True)
    session_pool = sessionmaker(bind=engine)
    with session_pool() as session:
        stmt = delete(OrderProduct)
        session.execute(stmt)
        stmt = delete(Order)
        session.execute(stmt)
        stmt = delete(Product)
        session.execute(stmt)
        stmt = delete(User)
        session.execute(stmt)
        session.commit()

    with session_pool() as session:
        repo = Repo(session)
        seed_fake_data(repo)



