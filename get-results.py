import pandas as pd
from semanticscholar import SemanticScholar
import time
import re
import os
import pickle
import csv

if os.path.exists("author_cache.pkl"):
    with open("author_cache.pkl", "rb") as f:
        author_cache = pickle.load(f)
else:
    author_cache = {}

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

# set up semantic scholar client
sch = SemanticScholar()
results = []

def normalize_name(name):
    # add a space before capital letters that follow lowercase letters (e.g., DemkeBrown → Demke Brown)
    return re.sub(r'(?<=[a-z])([A-Z])', r' \1', name).strip()

write_headers = not os.path.exists(csv_file)
csv_output = open(csv_file, "a", newline="", encoding="utf-8")
csv_writer = csv.DictWriter(csv_output, fieldnames=["Name", "DG_Year", "DG_Amount", "Publications_6Yrs", "Citations_6Yrs"])
if write_headers:
    csv_writer.writeheader()


# query each researcher
for _, row in df.iterrows():
    name = row["Name"]
    search_name = normalize_name(name)
    dg_year = row["DG_Year"]
    dg_amount = row["DG_Amount"]

    try:
        if search_name in author_cache:
            print(f"Using cached data for {search_name}")
            best_author = author_cache[search_name]
        else:
            author_matches = sch.search_author(search_name)
            if not author_matches:
                print(f"No match found for {search_name}")
                continue

            best_author = None
            max_pubs = -1

            for author in author_matches:
                try:
                    author_id = author['authorId']
                    author_data = sch.get_author(author_id)
                    time.sleep(0.5)

                    paper_count = len(author_data.papers) if author_data.papers else 0

                    if paper_count > max_pubs:
                        max_pubs = paper_count
                        best_author = author_data

                except Exception as inner_e:
                    print(f"Error loading author data: {inner_e}")
                    continue

            if best_author is None:
                print(f"No valid author data for {name}")
                continue

            # save to cache immediately
            author_cache[search_name] = best_author
            with open("author_cache.pkl", "wb") as f:
                pickle.dump(author_cache, f)
            print(f"Cached and saved author data for {search_name}")

        # filter publications from 6 years before DG year
        start_year = dg_year - 6
        end_year = dg_year - 1

        pub_count = 0
        citation_total = 0

        for paper in best_author.papers:
            pub_year = paper.year
            if pub_year and start_year <= pub_year <= end_year:
                pub_count += 1
                citation_total += paper.citationCount

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

