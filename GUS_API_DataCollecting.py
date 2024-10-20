import time
import requests
import pandas as pd


def getDataFromAPI(url, header):
    """
    Retrieves data from the API at the specified URL using the given header.
    If the request is successful, the response is returned as a dictionary.
    If an error occurs, a message is printed with the status code.
    """
    # Send a GET request to the specified URL
    response = requests.get(url, headers=header)

    # if the request was not successful, print the error
    if response.status_code != 200:
        print("Error occurred:", response.status_code)
    else:
        # if the request was successful, return the response as a dictionary
        return response.json().items()


if __name__ == '__main__':

    # API address for retrieving information about groups (for example: 0-4 years old males)
    url = "https://bdl.stat.gov.pl/api/v1/variables?subject-id=P2137&page=0&page-size=60"

    # API key with header
    header = {"X-ClientId": "YOUR PRIVATE API KEY"}

    # using function to retrieve data from API
    data = getDataFromAPI(url, header)

    # creating empty lists for groups ids and names
    group_id = []
    group_name = []
    # iterating threw data in dictionary to extract groups ids and names
    for key, values in data:
        if key == 'results':
            for i in range(len(values)):
                # appending data to specified lists
                group_id.append(values[i]['id'])
                group_name.append(values[i]['n1'] + " " + values[i]['n2'])

    # API address containing info about regions
    url = "https://bdl.stat.gov.pl/api/v1/Units?level=2&page-size=20"

    # using function to retrieve data from API
    data = getDataFromAPI(url, header)

    # creating empty lists for regions ids and names
    region_id = []
    region_name = []
    # iterating through data in dictionary to extract region IDs and names
    for key, values in data:
        if key == "results":
            for i in range(len(values)):
                # appending data to specified lists
                region_id.append(values[i]['id'])
                region_name.append(values[i]['name'])

    # iterating through years from 2002 to 2021
    for year in range(2002, 2022):
        # creating a list of empty lists, with one empty list for each region id
        population_by_group = [[] for i in range(len(region_id))]
        # initializing counter
        z = 0

        # iterating through region_id and group_id
        for i in region_id:
            for j in group_id:
                # building the API URL using the current year, region_id and group_id
                url = f"https://bdl.stat.gov.pl/api/v1/data/by-unit/{i}?var-id={j}&year={year}"
                # using function to retrieve data from API
                data = getDataFromAPI(url, header)
                # sleep to avoid overloading the API
                time.sleep(0.5)
                # iterating through the results in the response
                for key, values in data:
                    if key == 'results':
                        # iterating through the values in the results
                        for k in range(len(values)):
                            # appending the population data to the population_by_group list
                            population_by_group[z].append(values[k]['values'][0]['val'])

            # increment the counter
            z += 1

        # creating dataframes with pandas
        regions_df = pd.DataFrame({"Wojewodztwo": region_name, "Rok": year})
        population_df = pd.DataFrame(population_by_group, columns=group_name)

        # combining dataframes to one
        population_by_region_df = pd.concat([regions_df, population_df], axis=1)

        # saving new dataframe to csv file
        population_by_region_df.to_csv(f"population_by_region_{year}.csv")
        # after every successful export input confirmation
        print(f"File saved: population_by_region_{year}.csv")

        # dropping all the data from DataFrames to use them again in the next loop
        regions_df = regions_df.iloc[0:0]
        population_df = population_df.iloc[0:0]
        population_by_region_df = population_by_region_df.iloc[0:0]
