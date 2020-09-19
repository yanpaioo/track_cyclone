import re
from sqlalchemy import create_engine, Table, Column, Integer, String,\
    DateTime, MetaData, ForeignKey, Float, UniqueConstraint
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert

# TODO: Apply a data abstraction layer above individual DB engines


class PostgreSQLEngine:
    def __init__(self, host="0.0.0.0", port=5432, db="postgres",
                 user="sqluser", password="sqlpassword", echo=False):
        self._host = host
        self._port = port
        self._db = db
        self._metadata = MetaData()

        # Tablenames
        self._ocean_tablename = "ocean"
        self._cyclone_tablename = "cyclone"
        self._activity_tablename = "activity"

        # Tables
        self._ocean = Table(
            self._ocean_tablename,
            self._metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False, unique=True))

        self._cyclone = Table(
            self._cyclone_tablename,
            self._metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(100), nullable=False, unique=True))

        self._activity = Table(
            self._activity_tablename,
            self._metadata,
            Column("id", Integer, primary_key=True),
            Column("cyclone", ForeignKey("cyclone.name"), index=True),
            Column("timestamp", DateTime, nullable=False, index=True),
            Column("ocean", ForeignKey("ocean.name")),
            Column("latitude", Float),
            Column("longitude", Float),
            Column("intensity", Integer),
            UniqueConstraint("cyclone", "timestamp",
                             name="cyclone_and_timestamp_constraint")
        )

        self._engine = create_engine(
            f"postgresql+pg8000://{user}:{password}@{host}:{port}/{db}",
            echo=echo)
        self._metadata.create_all(self._engine)
        self._conn = self._engine.connect()

    def insert_ocean(self, name):
        ins = insert(self._ocean).values(name=self._format_name(name)).\
            on_conflict_do_nothing()
        self._conn.execute(ins)

    def select_all_ocean(self):
        ins = select([self._ocean])
        results = self._conn.execute(ins)
        return [dict(row) for row in results]

    def insert_cyclone(self, name):
        ins = insert(self._cyclone).\
            values(name=self._format_name(name)).\
            on_conflict_do_nothing()
        self._conn.execute(ins)

    def select_all_cyclone(self):
        ins = select([self._cyclone])
        results = self._conn.execute(ins)
        return [dict(row) for row in results]

    def insert_cyclone_activity(self, cyclone, datetime, ocean,
                                latitude, longitude, intensity):
        ins = insert(self._activity).values(
            cyclone=self._format_name(cyclone),
            timestamp=datetime,
            ocean=self._format_name(ocean),
            latitude=latitude,
            longitude=longitude,
            intensity=intensity
        ).on_conflict_do_nothing()
        self._conn.execute(ins)

    def select_activity(self, start_time=None, end_time=None, ocean=None):
        ins = select([self._activity])
        if start_time:
            ins = ins.where(self._activity.c.timestamp >= start_time)
        if end_time:
            ins = ins.where(self._activity.c.timestamp <= end_time)
        if ocean:
            ins = ins.where(self._activity.c.ocean == ocean)
        results = self._conn.execute(ins)
        return [dict(row) for row in results]

    @staticmethod
    def _format_name(name):
        return re.sub("[^0-9a-zA-Z]+", "-", name.lower())

    @property
    def handler(self):
        return self
