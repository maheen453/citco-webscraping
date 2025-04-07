import pandas as pd
from semanticscholar import SemanticScholar
import time

xls_file = "NSERC_Results_1743987822.xls"

# load all tables from the file
df_list = pd.read_html(xls_file)
df = df_list[0]  # take the first table

# clean column names
df.columns = df.columns.str.strip()

# extract start year (e.g., 2020 from 2020–2021)
df["DG_Year"] = df["Fiscal Year"].astype(str).str.extract(r"(\d{4})").astype(int)

# keep only the first grant per person
dg_df = df.sort_values(by=["Name", "DG_Year"]).drop_duplicates(subset="Name", keep="first")

# set up semantic scholar client
sch = SemanticScholar()
results = []

# query each researcher
for _, row in dg_df.iterrows():
    name = row["Name"]
    dg_year = row["DG_Year"]

    try:
        # search for the author
        author_matches = sch.search_author(name)
        if not author_matches:
            print(f"❌ No match found for {name}")
            continue

        author_id = author_matches[0]['authorId']
        author_data = sch.get_author(author_id)

        # filter publications from 6 years before DG year
        start_year = dg_year - 6
        end_year = dg_year - 1

        pub_count = 0
        citation_total = 0

        for paper in author_data.papers:
            pub_year = paper.year
            if pub_year and start_year <= pub_year <= end_year:
                pub_count += 1
                citation_total += paper.citationCount

        results.append({
            "Name": name,
            "DG_Year": dg_year,
            "Publications_6Yrs": pub_count,
            "Citations_6Yrs": citation_total
        })

        print(f"✅ {name}: {pub_count} pubs, {citation_total} citations")
        time.sleep(1)  # pause to avoid rate limiting

    except Exception as e:
        print(f"⚠️ Error with {name}: {e}")
        continue

# save to csv for statistical tests
out_df = pd.DataFrame(results)
out_df.to_csv("citation_pubs", index=False)
print("Saved results to citation_pubs.csv")
