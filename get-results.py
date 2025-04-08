import pandas as pd
from semanticscholar import SemanticScholar
import time

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

# make sure field of study is computer science
def is_computer_science_author(topics):
    if not topics:
        return False
    for topic in topics:
        if "computer science" in topic["topic"].lower():
            return True
    return False

# query each researcher
for _, row in df.iterrows():
    name = row["Name"]
    dg_year = row["DG_Year"]
    dg_amount = row["DG_Amount"]

    try:
        # search for the author
        author_matches = sch.search_author(name)
        if not author_matches:
            print(f"No match found for {name}")
            continue

        best_author = None
        max_pubs = -1

        for author in author_matches:
            try:
                author_id = author['authorId']
                author_data = sch.get_author(author_id)

                # If papers exist, check if this author has the most
                paper_count = len(author_data.papers) if author_data.papers else 0

                if paper_count > max_pubs:
                    max_pubs = paper_count
                    best_author = author_data
                time.sleep(0.5)  # avoid rate limiting

            except Exception as inner_e:
                print(f"Error loading author data: {inner_e}")
                continue

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

        results.append({
            "Name": name,
            "DG_Year": dg_year,
            "DG_Amount": dg_amount,
            "Publications_6Yrs": pub_count,
            "Citations_6Yrs": citation_total,
            
        })

        print(f"{name}: {pub_count} pubs, {citation_total} citations")
        time.sleep(1)  # pause to avoid rate limiting

    except Exception as e:
        print(f"Error with {name}: {e}")
        continue

# save to csv for statistical tests
out_df = pd.DataFrame(results)
out_df.to_csv("citation_pubs", index=False)
print("Saved results to citation_pubs.csv")
