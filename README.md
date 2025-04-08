# Citco Web Scraping Project

## Authors
Maarya Siddiqui	501159595
Maheen Qayyum	501202622
Rida Zafar		501192233
Riyan Kassam		501168357
Tasnuva Sayed	501172437

## 📌 Overview

Web scraping is a popular technique used to collect data from websites for further analysis and manipulation. This project employs web scraping using the **Semantic Scholar API** to determine whether there is a **correlation between the value of a researcher's Discovery Grant (DG)** and the **citation count** for their respective publications in the last 15 years, using information from the **Natural Sciences and Engineering Research Council of Canada (NSERC)** website.

Statistical tests were performed using the **SciPy** library to calculate the **correlation coefficient, R**, between the two datasets.

> This project specifically explores correlations within **Computer Science programs in Canadian universities**. However, the code can easily be modified to explore other fields of study.

---

## ✨ Features

### 🧾 NSERC Data Extraction
- NSERC data was manually extracted and stored in an `.xls` file.
- Filters used:
  - **Competition Year:** From 2008 to 2023  
  - **Institution & Province:** Universities  
  - **Area of Application:** Computer Software  
  - **Program:** Discovery Grants Program - Individual  

### 🔍 Semantic Scholar Data Extraction
- The **Semantic Scholar API** was used for automated data retrieval.
- Filters:
  - **Publication Year:** 2008–2023  
  - **Institution Affiliation:** Researchers affiliated with Canadian universities  
  - **Field of Study:** Computer Science  

---

## ⚙️ Installation

1. Open your terminal and navigate to the desired directory (e.g., Desktop):
   ```bash
   git clone https://github.com/maheen453/citco-webscraping
   cd citco-webscraping
   pip install -r requirements.txt



## Licensing
This project is licensed under the CPS406-MIT license version. 
