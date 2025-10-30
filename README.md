# plp-python-lastweek-ass

---

## 🎯 Project Objectives

1. Load and explore the **CORD-19 metadata.csv** dataset.
2. Clean and prepare the data for analysis.
3. Perform exploratory data analysis (EDA) to find patterns and trends.
4. Create visualizations using **Matplotlib** and **Seaborn**.
5. Build an interactive **Streamlit app** for data exploration.
6. Document and reflect on the data science workflow.

---

## 🧰 Tools and Libraries Used

- **Python 3.x**
- **Pandas** — for data manipulation
- **Matplotlib** and **Seaborn** — for visualizations
- **WordCloud** — for title word frequency visualization
- **NLTK** — for text preprocessing
- **Streamlit** — for building the interactive web app

📊 Dataset Description

Dataset Name: CORD-19 metadata

Source: COVID-19 Open Research Dataset (CORD-19)

File Used: metadata.csv

Content: Contains publication metadata on COVID-19 and coronavirus research papers.

Example Columns:

cord_uid – Unique paper ID

title – Paper title

abstract – Paper abstract

publish_time – Publication date

journal – Journal name

doi – Digital Object Identifier

🧹 Step-by-Step Process
Part 1: Data Loading and Exploration

Loaded the metadata.csv file into a Pandas DataFrame.

Inspected dimensions, data types, and missing values.

Generated basic summary statistics.

Part 2: Data Cleaning and Preparation

Handled missing values by dropping or filling.

Converted publish_time to datetime and extracted publication year.

Created a new feature: abstract_word_count.

Removed columns with >90% missing data.

Part 3: Data Analysis and Visualization

Counted papers per publication year.

Identified top publishing journals.

Extracted and visualized the most frequent words in titles.

Created bar charts and optional word clouds.

Part 4: Streamlit Web Application

Built a simple web app with:

Year range filter

Journal selector

Bar charts of publications and top journals

Interactive data table preview
