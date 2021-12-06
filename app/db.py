from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base


class DB:
    """Hosts all functions for querying the database."""
    def __init__(self, app):
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
        print("Creating all tables")
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.Session = sessionmaker(bind=self.engine)
        Session = self.Session()
        Session.commit()

                
        # attempt at direct read--has since been extracted up a level to __init__ for create and load
        # file = open(app.config['SQL_LOAD_PATH'])
        # abspath = getcwd()
        # escaped_sql = text(file.read().replace("$PATH$", abspath))
        # with self.engine.connect() as conn:
        #     conn.execute(escaped_sql)


    def connect(self):
        return self.engine.connect()

    def execute(self, sqlstr, **kwargs):
        """Execute sqlstr and return a list of result tuples.  sqlstr will be
        wrapped automatically in a
        sqlalchemy.sql.expression.TextClause.  You can use :param
        inside sqlstr and supply its value as a kwarg.  See
        https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.execute
        https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.text
        https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.CursorResult
        for additional details.  See models/*.py for examples of
        calling this function."""
        with self.engine.connect() as conn:
            return list(conn.execute(text(sqlstr), kwargs).fetchall())

    def execute_no_return(self, sqlstr, **kwargs):
        with self.engine.connect() as conn:
            conn.execute(text(sqlstr), kwargs)
