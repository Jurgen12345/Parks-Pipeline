import sqlite3
import pandas as pd
from pathlib import Path
import os
import duckdb
import time


class Preprocessor:
    visitorSpending_directory = fr"{os.getcwd()}\bronze\parks\visitor_spending"
    visitors_directory = fr"{os.getcwd()}\bronze\parks\visitors"
    visits_directory = fr"{os.getcwd()}\bronze\parks\visits"

    current_dir = Path(__file__).resolve().parent
    output_path = current_dir / "silver" / "parks"
    output_path.mkdir(parents=True, exist_ok=True)

    def __init__(self):
        (self.output_path / "visits").mkdir(parents=True, exist_ok=True)
        (self.output_path / "visitor_spending").mkdir(parents=True, exist_ok=True)
        (self.output_path / "visit_activities").mkdir(parents=True, exist_ok=True)
        (self.output_path / "visit_days").mkdir(parents=True, exist_ok=True)
        (self.output_path / "visitors").mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect((self.current_dir / "duckLake.duckdb").as_posix())

        lite_conn = sqlite3.connect("preprocessorMetadata.db")
        cur = lite_conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS preprocessorMetadata(
                last_updated_file TEXT
            )
        """)

        last_date = cur.execute("""
            SELECT last_updated_file FROM preprocessorMetadata
        """).fetchone()

        if last_date is None:
            cur.execute("""
                INSERT INTO preprocessorMetadata (last_updated_file)
                VALUES (?)
            """, ("run=0",))
            lite_conn.commit()

        while True:
            checking_path = self.current_dir / "bronze" / "parks" / "visits"
            folders = sorted([folder for folder in checking_path.iterdir() if folder.is_dir()])

            last_value = cur.execute("""
                SELECT last_updated_file FROM preprocessorMetadata
            """).fetchone()[0]

            last_run_value = last_value.split("=")[1]

            for date in range(len(folders)):
                dt_folder = folders[date]
                run_folders = sorted([folder for folder in dt_folder.iterdir() if folder.is_dir()])

                for index in range(len(run_folders)):
                    run_folder = run_folders[index]
                    run_value = run_folder.name.split("=")[1]

                    if run_value <= last_run_value:
                        continue

                    print("DT:", dt_folder.name)
                    print("RUN:", run_folder.name)

                    current_run_folder_visits = self.current_dir / "bronze" / "parks" / "visits" / dt_folder.name / run_folder.name
                    current_run_folder_visit_activities = self.current_dir / "bronze" / "parks" / "visit_activities" / dt_folder.name / run_folder.name
                    current_run_folder_visit_days = self.current_dir / "bronze" / "parks" / "visit_days" / dt_folder.name / run_folder.name
                    current_run_folder_visitor_spending = self.current_dir / "bronze" / "parks" / "visitor_spending" / dt_folder.name / run_folder.name
                    current_run_folder_visitors = self.current_dir / "bronze" / "parks" / "visitors" / dt_folder.name / run_folder.name

                    try:
                        visits_file = next(current_run_folder_visits.glob("*.json"))
                        visit_activities_file = next(current_run_folder_visit_activities.glob("*.json"))
                        visit_days_file = next(current_run_folder_visit_days.glob("*.json"))
                        visitor_spending_file = next(current_run_folder_visitor_spending.glob("*.json"))
                        visitors_file = next(current_run_folder_visitors.glob("*.json"))
                    except StopIteration:
                        print("Missing one or more JSON files for:", dt_folder.name, run_folder.name)
                        continue

                    try:
                        visit_activities_df = conn.execute(f"""
                            SELECT * FROM read_json_auto('{visit_activities_file.as_posix()}')
                        """).df()

                        visits_df = conn.execute(f"""
                            SELECT * FROM read_json_auto('{visits_file.as_posix()}')
                        """).df()

                        visit_days_df = conn.execute(f"""
                            SELECT * FROM read_json_auto('{visit_days_file.as_posix()}')
                        """).df()

                        visitor_spending_df = conn.execute(f"""
                            SELECT * FROM read_json_auto('{visitor_spending_file.as_posix()}')
                        """).df()

                        visitors_df = conn.execute(f"""
                            SELECT * FROM read_json_auto('{visitors_file.as_posix()}')
                        """).df()
                    except Exception as e:
                        print("Error reading JSON for:", dt_folder.name, run_folder.name)
                        print(e)
                        continue

                    visits_df = visits_df.dropna()
                    visitor_spending_df = visitor_spending_df.dropna()
                    visitors_df = visitors_df.dropna()

                    visits_out_dir = self.output_path / "visits" / dt_folder.name / run_folder.name
                    visitor_spending_out_dir = self.output_path / "visitor_spending" / dt_folder.name / run_folder.name
                    visit_activities_out_dir = self.output_path / "visit_activities" / dt_folder.name / run_folder.name
                    visit_days_out_dir = self.output_path / "visit_days" / dt_folder.name / run_folder.name
                    visitors_out_dir = self.output_path / "visitors" / dt_folder.name / run_folder.name

                    visits_out_dir.mkdir(parents=True, exist_ok=True)
                    visitor_spending_out_dir.mkdir(parents=True, exist_ok=True)
                    visit_activities_out_dir.mkdir(parents=True, exist_ok=True)
                    visit_days_out_dir.mkdir(parents=True, exist_ok=True)
                    visitors_out_dir.mkdir(parents=True, exist_ok=True)

                    try:
                        visits_df.to_parquet(visits_out_dir / f"{visits_file.stem}.parquet", index=False)
                        visitor_spending_df.to_parquet(visitor_spending_out_dir / f"{visitor_spending_file.stem}.parquet", index=False)
                        visit_activities_df.to_parquet(visit_activities_out_dir / f"{visit_activities_file.stem}.parquet", index=False)
                        visit_days_df.to_parquet(visit_days_out_dir / f"{visit_days_file.stem}.parquet", index=False)
                        visitors_df.to_parquet(visitors_out_dir / f"{visitors_file.stem}.parquet", index=False)
                    except Exception as e:
                        print("Error writing parquet for:", dt_folder.name, run_folder.name)
                        print(e)
                        continue

                    cur.execute("""
                        UPDATE preprocessorMetadata
                        SET last_updated_file = ?
                    """, (run_folder.name,))
                    lite_conn.commit()

                    last_run_value = run_value

                    last_value_now = cur.execute("""
                        SELECT last_updated_file FROM preprocessorMetadata
                    """).fetchone()

                    print("Updated checkpoint to:", last_value_now[0])

            time.sleep(5)


if __name__ == "__main__":
    p = Preprocessor()
