import requests
import time


class ParksPipeline:

    API_KEY = "yourAPIKey"
    CONSUMER_KEY = "yourConsumerKey"
    healthCheckURL = "https://msde630.class-labs.com/healthcheck"
    pollURL = f"https://msde630.class-labs.com/poll?consumer_key={CONSUMER_KEY}"
    continueFetching = True


    def __init__(self):
        healthCheck = requests.get(url = self.healthCheckURL, headers={'accept': 'application/json'}, timeout=(10, 30),)
        if healthCheck.status_code == 200:
            checks = healthCheck.json()["checks"]
            databaseStatus = checks["database"]["status"].lower()
            datarefreshStatus = checks["data_refresh"]["status"].lower()
            if databaseStatus == "ok" and datarefreshStatus == "ok":
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

            else:
                print("API backend is unstable!")
                print(f"Database Status: {databaseStatus}")
                print(f"Data Refresh Status: {datarefreshStatus}")

        else:
            print(f"There was a problem with the health check endpoint connection that resulted in the status code: {healthCheck.status_code}")


if __name__ == "__main__":
    parksOne = ParksPipeline()