import duckdb
import time

class ParksDimensionalModel:

    sql ="""
DROP TABLE IF EXISTS daily_spend_category_fact;
DROP TABLE IF EXISTS visit_dim;
DROP TABLE IF EXISTS spending_category_dim;
DROP TABLE IF EXISTS date_dim;

DROP SEQUENCE IF EXISTS spending_category_seq;
DROP SEQUENCE IF EXISTS visit_seq;
DROP SEQUENCE IF EXISTS daily_spend_fact_seq;

CREATE SEQUENCE spending_category_seq;
CREATE SEQUENCE visit_seq;
CREATE SEQUENCE daily_spend_fact_seq;

CREATE TABLE date_dim (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,

    weekday TEXT NOT NULL,
    weekday_short_name TEXT NOT NULL,
    weekday_num INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,

    month_name TEXT NOT NULL,
    month_name_short TEXT NOT NULL,
    month_num INTEGER NOT NULL,

    first_day_of_month DATE NOT NULL,
    last_day_of_month DATE NOT NULL,

    year INTEGER NOT NULL,
    season TEXT NOT NULL,
    seasonal_year INTEGER NOT NULL
);

CREATE TABLE spending_category_dim (
    spending_category_key BIGINT PRIMARY KEY DEFAULT nextval('spending_category_seq'),
    spending_category_id INTEGER NOT NULL UNIQUE,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE visit_dim (
    visit_key BIGINT PRIMARY KEY DEFAULT nextval('visit_seq'),
    visit_id INTEGER NOT NULL UNIQUE,

    park_id INTEGER NOT NULL,
    park_name TEXT NOT NULL,
    park_state TEXT NOT NULL,

    home_state TEXT NOT NULL,
    lodging_name TEXT NOT NULL,

    start_date_key_fk INTEGER NOT NULL,
    end_date_key_fk INTEGER NOT NULL,

    day_count INTEGER NOT NULL,

    FOREIGN KEY (start_date_key_fk) REFERENCES date_dim(date_key),
    FOREIGN KEY (end_date_key_fk) REFERENCES date_dim(date_key)
);

CREATE TABLE daily_spend_category_fact (
    daily_spend_category_fact_key BIGINT PRIMARY KEY DEFAULT nextval('daily_spend_fact_seq'),

    visit_key_fk BIGINT NOT NULL,
    date_key_fk INTEGER NOT NULL,
    spending_category_key_fk BIGINT NOT NULL,

    amount NUMERIC NOT NULL,

    FOREIGN KEY (visit_key_fk) REFERENCES visit_dim(visit_key),
    FOREIGN KEY (date_key_fk) REFERENCES date_dim(date_key),
    FOREIGN KEY (spending_category_key_fk)
        REFERENCES spending_category_dim(spending_category_key),

    UNIQUE (visit_key_fk, date_key_fk, spending_category_key_fk)
);

WITH RECURSIVE dates(d) AS (
    SELECT DATE '2024-01-01'
    UNION ALL
    SELECT CAST(d + INTERVAL 1 DAY AS DATE)
    FROM dates
    WHERE d < DATE '2026-12-31'
)
INSERT INTO date_dim (
    date_key,
    full_date,
    weekday,
    weekday_short_name,
    weekday_num,
    day_of_month,
    week_of_year,
    month_name,
    month_name_short,
    month_num,
    first_day_of_month,
    last_day_of_month,
    year,
    season,
    seasonal_year
)
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER),
    d,

    dayname(d),
    substr(dayname(d),1,3),
    CAST(strftime(d,'%u') AS INTEGER),
    EXTRACT(day FROM d),
    weekofyear(d),

    monthname(d),
    substr(monthname(d),1,3),
    EXTRACT(month FROM d),

    CAST(date_trunc('month',d) AS DATE),
    last_day(d),

    EXTRACT(year FROM d),

    CASE
        WHEN strftime(d,'%m-%d') BETWEEN '03-20' AND '06-19' THEN 'Spring'
        WHEN strftime(d,'%m-%d') BETWEEN '06-20' AND '09-21' THEN 'Summer'
        WHEN strftime(d,'%m-%d') BETWEEN '09-22' AND '12-20' THEN 'Autumn'
        ELSE 'Winter'
    END,

    CASE
        WHEN strftime(d,'%m-%d') < '03-20'
            THEN EXTRACT(year FROM d) - 1
        ELSE EXTRACT(year FROM d)
    END
FROM dates;
        """ 

    def __init__(self):
        conn = duckdb.connect("parks_gold.duckdb")
        while True:
            conn.execute("""
                         drop view if exists silver_visits;
                         drop view if exists silver_visitors;
                         drop view if exists silver_visit_days;
                         drop view if exists silver_visitor_spending;
                         drop view if exists silver_parks;
                         drop view if exists silver_lodging_types;
                         drop view if exists silver_spending_categories;
                         """)

            is_empty = conn.execute("""
                         select * from read_parquet('silver/parks/visits/**/*.parquet')
                         """).fetchone()

            if is_empty != None:


                conn.execute("""
                    CREATE OR REPLACE VIEW silver_visits AS
                    SELECT * FROM read_parquet('silver/parks/visits/**/*.parquet');

                    CREATE OR REPLACE VIEW silver_visitors AS
                    SELECT * FROM read_parquet('silver/parks/visitors/**/*.parquet');

                    CREATE OR REPLACE VIEW silver_visit_days AS
                    SELECT * FROM read_parquet('silver/parks/visit_days/**/*.parquet');

                    CREATE OR REPLACE VIEW silver_visitor_spending AS
                    SELECT * FROM read_parquet('silver/parks/visitor_spending/**/*.parquet');

                    CREATE OR REPLACE VIEW silver_parks AS
                    SELECT * FROM read_parquet('silver/parks/park/*.parquet');

                    CREATE OR REPLACE VIEW silver_lodging_types AS
                    SELECT * FROM read_parquet('silver/parks/lodging_type/*.parquet');

                    CREATE OR REPLACE VIEW silver_spending_categories AS
                    SELECT * FROM read_parquet('silver/parks/spending_categories/*.parquet');
                    """)
                    
                conn.execute(self.sql)

                conn.execute("""
                            insert into spending_category_dim (spending_category_id,category_name)
                            select distinct spending_category_id, category_name from silver_spending_categories;
                            """)
                conn.execute("""
                            insert into visit_dim(
                            visit_id,park_id,park_name,park_state,home_state,lodging_name,start_date_key_fk,
                            end_date_key_fk, day_count
                            )
                            select distinct
                                v.visit_id,
                                v.park_id,
                                p.park_name,
                                p.state AS park_state,
                                vis.home_state,
                                lt.lodging_name,
                                CAST(strftime(v.start_date, '%Y%m%d') AS INTEGER) AS start_date_key_fk,
                                CAST(strftime(v.end_date, '%Y%m%d') AS INTEGER) AS end_date_key_fk,
                                datediff('day', CAST(v.start_date AS DATE), CAST(v.end_date AS DATE)) + 1 AS day_count
                            from silver_visits v
                            join silver_visitors vis
                            on v.visitor_id = vis.visitor_id
                            join silver_parks p
                                on v.park_id = p.park_id
                            join silver_lodging_types lt
                                on v.lodging_type_id = lt.lodging_type_id;
                            """)

                conn.execute("""
                            insert into daily_spend_category_fact(
                                visit_key_fk,
                                date_key_fk,
                                spending_category_key_fk,
                                amount
                            )
                            select
                                vd.visit_key,
                                CAST(strftime(d.calendar_date, '%Y%m%d') AS INTEGER) AS date_key_fk,
                                scd.spending_category_key,
                                COALESCE(vs.amount, 0) AS amount
                            from silver_visitor_spending vs
                            join silver_visit_days d
                                ON vs.visit_day_id = d.visit_day_id
                            join visit_dim vd
                                ON vs.visit_id = vd.visit_id
                            join spending_category_dim scd
                                ON vs.spending_category_id = scd.spending_category_id;
                            """)


                print(conn.execute("DESCRIBE silver_visits").fetchdf())
                print(conn.execute("DESCRIBE silver_visitors").fetchdf())
                print(conn.execute("DESCRIBE silver_visit_days").fetchdf())
                print(conn.execute("DESCRIBE silver_visitor_spending").fetchdf())

                print(conn.execute("select * from daily_spend_category_fact").fetchdf())
            else:
                pass
            time.sleep(10)
            




if __name__ == "__main__":
    gold = ParksDimensionalModel()