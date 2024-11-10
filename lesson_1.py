from sqlalchemy import create_engine, URL

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

url = URL.create(
    drivername="postgresql+psycopg2",  # driver name = postgresql + the library we are using (psycopg2)
    username='testuser',
    password='testpassword',
    host='localhost',
    database='testuser',
    port=5432
)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    engine = create_engine(url, echo=True)
    print(url.render_as_string())

    session_pool = sessionmaker(bind=engine)

    with session_pool() as session:
        query = text("""
    CREATE TABLE users
(
    telegram_id   BIGINT PRIMARY KEY,
    full_name     VARCHAR(255) NOT NULL,
    username      VARCHAR(255),
    language_code VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    referrer_id   BIGINT,
    FOREIGN KEY (referrer_id)
        REFERENCES users (telegram_id)
        ON DELETE SET NULL
);        
        """)
        session.execute(query)
        session.commit()


    with session_pool() as session:
        insert_query = text("""
        INSERT INTO users (telegram_id, full_name, username, language_code, referrer_id)
        VALUES (1, 'John Doe', 'johndoe', 'en', NULL),
                  (2, 'Jane Doe', 'janedoe', 'en', 1);
        """)
        session.execute(insert_query)
        session.commit()

        select_query = text("""
        SELECT * FROM users;
        """)
        result = session.execute(select_query)
        for row in result:
            print(row)
