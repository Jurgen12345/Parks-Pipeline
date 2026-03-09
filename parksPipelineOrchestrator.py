import subprocess
import sys
import time
from pathlib import Path
import os
import requests
import json
import pandas as pd



class ParksPipelineOrchestrator:


    py = sys.executable
    programs = {
        "bronze":"parksPipelineCollector.py",
        "healthcheck":"parksCheckOccasionallyHealthCheck.py",
        "silver":"parksPipelinePreprocessor.py",
        "gold":"parksPipelineDimensionalModel.py"
    }
    def __init__(self):
        self.LOGS = Path("logs")
        self.LOGS.mkdir(exist_ok=True)
        procs = {}
        backoff = {name: 1 for name in self.programs}
        bprocess, bout, berr = self.start("bronze")
        collector_running = True
        hprocess, hout, herr = self.start("healthcheck")
        sprocess, sout, serr= self.start("silver")
        gprocess, gout, gerr = self.start("gold")
        self.collectStatic()
        while True:


            last_healthcheck_status = self.closecollector(hout)
            if last_healthcheck_status != "1" and collector_running:
                print(f"At {time.ctime()} the backend database is not unstable. Stopping collector. Healthcheck status : {last_healthcheck_status}")
                bprocess.kill()
                bprocess.wait()
                bout.close()
                berr.close()
                collector_running = False
            elif last_healthcheck_status == "1" and not collector_running:
                print(f"At {time.ctime()} the backend database is stable. Starting collector again. Healthcheck status : {last_healthcheck_status}")
                bprocess, bout, berr = self.start("bronze")
                collector_running = True

            for name in self.programs:
                err_path = self.LOGS / f"{name}.err.log"
                with open(err_path, "r",encoding="utf-8") as file:
                    content = file.read()
                    if content.strip():
                        print(f"At time : {time.ctime()}/ There was an error on the {name} layer!!Restarting.")
                        print(f"Error message :{content}")
                        if name == "bronze" and collector_running:
                            bprocess.kill()
                            bprocess.wait()
                            bout.close()
                            berr.close()
                            bprocess, bout, berr = self.start(name)
                        elif name == "silver":
                            sprocess.kill()
                            sprocess.wait()
                            sout.close()
                            serr.close()
                            sprocess, sout, serr = self.start(name)
                        elif name == "healthcheck":
                            hprocess.kill()
                            hprocess.wait()
                            hout.close()
                            herr.close()
                            hprocess,hout,herr = self.start(name)
                        elif name == "gold":
                            gprocess.kill()
                            gprocess.wait()
                            gout.close()
                            gerr.close()
                            gprocess, gout, gerr = self.start(name)

            time.sleep(3)


    def collectStatic(self):
        LOGS_LODGIN_TYPES_BRONZE = Path(r"bronze/parks/lodging_type")
        LOGS_LODGIN_TYPES_BRONZE.mkdir(parents=True, exist_ok=True)
        LOGS_LODGIN_TYPES_SILVER = Path(r"silver/parks/lodging_type")
        LOGS_LODGIN_TYPES_SILVER.mkdir(parents=True, exist_ok=True)

        LOGS_PARK_BRONZE= Path(r"bronze/parks/park")
        LOGS_PARK_BRONZE.mkdir(parents=True, exist_ok=True)
        LOGS_PARK_SILVER =Path(r"silver/parks/park")
        LOGS_PARK_SILVER.mkdir(parents=True, exist_ok=True)

        LOGS_SPENDING_CATEGORY_BRONZE = Path(r"bronze/parks/spending_categories")
        LOGS_SPENDING_CATEGORY_BRONZE.mkdir(parents=True, exist_ok=True)
        LOGS_SPENDING_CATEGORY_SILVER= Path(r"silver/parks/spending_categories")
        LOGS_SPENDING_CATEGORY_SILVER.mkdir(parents=True, exist_ok=True)

        url = "https://msde630.class-labs.com/static-data"
        headers = {"accept" : "application/json"}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            parks_data = r.json()["parks"]
            lodging_type_data = r.json()["lodging_types"]
            spending_categories_data = r.json()["spending_categories"]
            if not (LOGS_PARK_BRONZE / "parks.json").exists():
                with open(LOGS_PARK_BRONZE / "parks.json", "w",encoding="utf-8") as file:
                    json.dump(parks_data, file, indent=2)
            if not (LOGS_LODGIN_TYPES_BRONZE / "lodging_types.json").exists():
                with open(LOGS_LODGIN_TYPES_BRONZE / "lodging_types.json" , "w", encoding="utf-8") as file:
                    json.dump(lodging_type_data, file, indent=2)
            if not (LOGS_SPENDING_CATEGORY_BRONZE / "spending_categories.json").exists():
                with open(LOGS_SPENDING_CATEGORY_BRONZE / "spending_categories.json", "w", encoding="utf-8") as file:
                    json.dump(spending_categories_data, file)
            if not (LOGS_PARK_SILVER / "parks.parquet").exists():
                pd.DataFrame(parks_data).to_parquet(LOGS_PARK_SILVER / "parks.parquet", index=False)
            if not (LOGS_LODGIN_TYPES_SILVER / "lodging_types.parquet").exists():
                pd.DataFrame(lodging_type_data).to_parquet(LOGS_LODGIN_TYPES_SILVER / "lodging_types.parquet",index=False)
            if not (LOGS_SPENDING_CATEGORY_SILVER / "spending_categories.parquet").exists():
                pd.DataFrame(spending_categories_data).to_parquet(LOGS_SPENDING_CATEGORY_SILVER / "spending_categories.parquet", index = False)


        elif r.status_code == 401:
            print("Not Authenticated. Please enter the correct api key.")




    def closecollector(self,output):
        while True:
            with open(output.name, "r", encoding="utf-8") as file:
                lines = file.readlines()
            last_status = next(
                (l.strip() for l in reversed(lines) if l.strip() and "START healthcheck pid=" not in l),
                None 
            )
            return last_status

    def start(self,name):
        base_dir = Path(__file__).resolve().parent
        out = open(self.LOGS  / f"{name}.out.log", "a", buffering=1, encoding="utf-8")
        err = open(self.LOGS / f"{name}.err.log", "w", buffering=1,encoding="utf-8")
        process = subprocess.Popen([self.py, "-u", self.programs[name]], stdout  = out, stderr=err, cwd=base_dir)
        out.write(f"\n[{time.ctime()}] START {name} pid= {process.pid}\n")
        return process, out,err 

if __name__ =="__main__":
    orchestrator = ParksPipelineOrchestrator()

