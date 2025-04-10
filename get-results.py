import pandas as pd
import time
import re
import os
import pickle
import csv
import requests

# setting up api
limit = 1000
api_url = "https://api.semanticscholar.org/graph/v1/author/"
fields = "name,papers.title,papers.year,papers.citationCount"

# if the author has been queried before it'll be in cache
if os.path.exists("author_cache.pkl"):
    with open("author_cache.pkl", "rb") as f:
        author_cache = pickle.load(f)
else:
    author_cache = {}

# track already processed names to skip them in future runs
processed_names = set()
csv_file = "citation_pubs.csv"
if os.path.exists(csv_file):
    existing_df = pd.read_csv(csv_file)
    processed_names = set(existing_df["Name"].unique())

xls_file = "NSERC_Results.xls"

# load all tables from the file
df_list = pd.read_html(xls_file)
df = df_list[0]  # take the first table

# clean column names
df.columns = df.columns.str.strip()

# extract start year (e.g., 2020 from 2020–2021)
df["DG_Year"] = df["Fiscal Year"].astype(str).str.extract(r"(\d{4})").astype(int)

#extract DG amount
df["DG_Amount"] = df["Amount($)"].astype(str).str.replace(",", "").str.extract(r"(\d+)").astype(float)

# set up csv writer
write_headers = not os.path.exists(csv_file)
csv_output = open(csv_file, "a", newline="", encoding="utf-8")
csv_writer = csv.DictWriter(csv_output, fieldnames=["Name", "DG_Year", "DG_Amount", "Publications_6Yrs", "Citations_6Yrs"])
if write_headers:
    csv_writer.writeheader()


def normalize_name(name):
    # add a space before capital letters that follow lowercase letters (e.g., DemkeBrown → Demke Brown)
    return re.sub(r'(?<=[a-z])([A-Z])', r' \1', name).strip()

# get all papers for a given author using paginated API requests and retry if certain errors occur
def get_author_with_limit(author_id, limit=100):
    all_papers = []
    offset = 0
    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "fields": "title,year,citationCount"
        }
        url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"
        for attempt in range(5):
            response = requests.get(url, params=params)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                sleep_time = 2 ** attempt
                print(f"Rate limit hit (papers fetch). Sleeping for {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise Exception(f"API error {response.status_code}: {response.text}")
        else:
            raise Exception("Max retries exceeded while fetching papers.")

        data = response.json()
        new_papers = data.get("data", [])
        if not new_papers:
            break
        all_papers.extend(new_papers)
        offset += limit
        time.sleep(0.5)  
    return all_papers



# query each researcher
for _, row in df.iterrows():
    name = row["Name"]
    if name in processed_names:
        print(f"Already processed {name}, skipping.")
        continue

    search_name = normalize_name(name)
    dg_year = row["DG_Year"]
    dg_amount = row["DG_Amount"]

    try:
        if search_name in author_cache:
            print(f"Using cached data for {search_name}")
            author_id = author_cache[search_name]["authorId"]
        else:
            search_url = "https://api.semanticscholar.org/graph/v1/author/search"
            search_params = {"query": search_name, "limit": 5}
            for attempt in range(5):
                response = requests.get(search_url, params=search_params)
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    sleep_time = 2 ** attempt
                    print(f"Rate limit hit (search). Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    raise Exception(f"Search failed: {response.status_code} - {response.text}")
            else:
                raise Exception("Max retries exceeded during author search.")

            data = response.json()

            author_matches = data.get("data", [])
            if not author_matches:
                print(f"No match found for {search_name}")
                continue

            best_match = max(author_matches, key=lambda x: x.get("paperCount", 0))
            author_id = best_match["authorId"]
            author_cache[search_name] = {"authorId": author_id}
            with open("author_cache.pkl", "wb") as f:
                pickle.dump(author_cache, f)
            print(f"Cached author ID for {search_name}")

        papers = get_author_with_limit(author_id, limit=1000)

        # filter publications from 6 years before DG year
        start_year = dg_year - 6
        end_year = dg_year - 1

        pub_count = 0
        citation_total = 0

        for paper in papers:
            pub_year = paper.get("year")
            if pub_year and start_year <= pub_year <= end_year:
                pub_count += 1
                citation_total += paper.get("citationCount", 0)


        result_row = {
            "Name": name,
            "DG_Year": dg_year,
            "DG_Amount": dg_amount,
            "Publications_6Yrs": pub_count,
            "Citations_6Yrs": citation_total,
        }
        csv_writer.writerow(result_row)
        csv_output.flush() 

        print(f"{name}: {pub_count} pubs, {citation_total} citations")
        time.sleep(1)  # pause to avoid rate limiting

    except Exception as e:
        print(f"Error with {name}: {e}")
        continue

# save to csv for statistical tests
csv_output.close()
print("Done! All data saved to citation_pubs.csv")

