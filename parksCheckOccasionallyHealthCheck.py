import sqlite3
import requests
import time

class Connection:
    healthCheckURL = "https://msde630.class-labs.com/healthcheck"
    def __init__(self):
        self.conn = sqlite3.connect("healthcheck.db")
        self.cur = self.conn.cursor()

        self.cur.execute("""
                    Create table if not exists pipeline_healthcheck(
                        backend_stable text
                    )
                    """)

        self.conn.commit()


        while True:
            self.cur.execute("""
                        select backend_stable from pipeline_healthcheck;
                        """)

            self.conn.commit()
            row = self.cur.fetchone()           
            if row != None:
                print(row[0])
                self.runHealthCheck()
                self.cur.execute("""
                        select backend_stable from pipeline_healthcheck;
                                """)
            elif row == None:
                self.runHealthCheckFirstTime()                  
                self.cur.execute("""
                        select backend_stable from pipeline_healthcheck;
                        """)
                self.conn.commit()
                print(row[0])

            time.sleep(90)
            
        self.conn.close()




    def runHealthCheckFirstTime(self):
        healthCheck = requests.get(url = self.healthCheckURL, headers={'accept': 'application/json'}, timeout=(10, 30),)
        if healthCheck.status_code == 200:
            checks = healthCheck.json()["checks"]
            databaseStatus = checks["database"]["status"].lower()
            datarefreshStatus = checks["data_refresh"]["status"].lower()
            if databaseStatus == "ok" and datarefreshStatus== "ok":
                self.cur.execute("""
                    insert into pipeline_healthcheck (backend_stable) values('1') 
                """) 
                self.conn.commit()
            else:
                self.cur.execute("""
                    insert into pipeline_healthcheck (backend_stable) values('0')
                                 """)
                self.conn.commit()
        else:
            pass


    def runHealthCheck(self):
        healthCheck = requests.get(url = self.healthCheckURL, headers={'accept': 'application/json'}, timeout=(10, 30),)
        if healthCheck.status_code == 200:
            checks = healthCheck.json()["checks"]
            databaseStatus = checks["database"]["status"].lower()
            datarefreshStatus = checks["data_refresh"]["status"].lower()
            if databaseStatus == "ok" and datarefreshStatus== "ok":
                self.cur.execute("""
                    update pipeline_healthcheck set backend_stable = '1' 
                """) 
                self.conn.commit()
            else:
                self.cur.execute("""
                    update pipeline_healthcheck set backend_stable = '0'
                                 """)
                self.conn.commit()
        else:
            pass


if __name__ == "__main__":
    a = Connection()