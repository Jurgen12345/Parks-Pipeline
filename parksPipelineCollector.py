import requests
import time
from pathlib import Path
import json
import datetime

class ParksPipeline:

    API_KEY = "parks_sk_jqAC9bnQiNTnO9hEmHg6_6qH_7kxjdhl6UoI_zIdlMY"
    CONSUMER_KEY = "HmBRdiQA9f2IrucAtuKWMTT-O4Njlke8"
    healthCheckURL = "https://msde630.class-labs.com/healthcheck"
    pollURL = f"https://msde630.class-labs.com/poll?consumer_key={CONSUMER_KEY}"
    continueFetching = True


    def __init__(self):
        
        tables = ["visits","visitors","visit_days","visit_activities","visitor_spending"]
        
        LOGS_VISTS = Path(r"bronze/parks/visits")
        LOGS_VISTS.mkdir(parents=True,exist_ok=True) 
        LOGS_VISITORS = Path(r"bronze/parks/visitors")
        LOGS_VISITORS.mkdir(parents=True,exist_ok=True)
        LOGS_VISITDAYS = Path(r"bronze/parks/visit_days")
        LOGS_VISITDAYS.mkdir(parents=True, exist_ok=True)
        LOGS_ACTIVITIES = Path(r"bronze/parks/visit_activities")
        LOGS_ACTIVITIES.mkdir(parents=True,exist_ok=True)
        LOGS_SPENDING = Path(r"bronze/parks/visitor_spending")
        LOGS_SPENDING.mkdir(parents=True, exist_ok=True)
               



        while self.continueFetching:
            startEventId = requests.get(url=self.pollURL, headers={
                'accept': 'application/json',
                'X-Api-Key': self.API_KEY 
                },timeout=(10, 30),)
            if startEventId.status_code == 200:
                maxEvents = startEventId.json()["end_event_id"]
                start = startEventId.json()["start_event_id"]
                end = start + 24
                print(f"Start Event ID : {start}")
                print(f"End Event Id : {end}")
                fetchingData = requests.get(url=f'https://msde630.class-labs.com/fetch?consumer_key={self.CONSUMER_KEY}&start_event_id={start}&end_event_id={end}',
                                        headers={'accept': 'application/json',
                                                'X-Api-Key': self.API_KEY },timeout=(10, 30),)
                print("Finished Fetching")
                if fetchingData.status_code == 200:
                    data = fetchingData.json()
                    print(len(data))
                    if len(data) > 0:
                        for table in tables:
                            LOGS = Path(f'bronze/parks/{table}/dt={datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")}/run={str(datetime.datetime.utcnow().strftime("%Y-%m-%d:%H:%M:%S").replace("-","").replace(":",""))}')
                            LOGS.mkdir(parents=True, exist_ok=True)
                            datafile= open(LOGS / f"start={start}_end={end}.json", "w",buffering=1, encoding="utf-8")
                            json.dump(data[table], datafile)
                            datafile.close()
                        commitEndpoint = requests.post(url = f'https://msde630.class-labs.com/commit?consumer_key=HmBRdiQA9f2IrucAtuKWMTT-O4Njlke8&event_id={end}',
                                                headers={
                                                    'accept': 'application/json',
                                                    'X-Api-Key': self.API_KEY},timeout=(10, 30),)
                        if commitEndpoint.status_code == 200:
                            print(f"The event id number {end} was commited successfully!")
                        else:
                            print(f"There was a problem with the commit endpoint connection that resulted in the status code : {commitEndpoint.status_code}")
                        time.sleep(15)
                    else:
                        print(f"The length of the data is {len(data)}")
                        pass
                else:
                        print(f"There was a problem with the fetch endpoint connection that resulted in the status code: {fetchingData.status_code}")
            else:
                    print(f"There was a problem with the poll endpoint connection that resulted in the status code: {startEventId.status_code}")


            

if __name__ == "__main__":
    parksOne = ParksPipeline()