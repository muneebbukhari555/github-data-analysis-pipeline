# GitHub Data Analysis Pipeline

## Overview

This project uses the GitHub API to collect repository data and analyze
it using Python. The main focus is to understand repository popularity,
activity, and trends.



## What this project does

-   Fetches data from GitHub API
-   Converts raw data into a structured format using Pandas
-   Cleans and processes the data
-   Creates new metrics like stars per day
-   Visualizes the results using graphs



## Tech used

-   Python
-   Pandas
-   MongoDB
-   GitHub API

## Project files

github_api_data.ipynb \# main notebook\
github_data.csv \# dataset\
main.py \# script version

## Key analysis

-   Compare repositories based on stars
-   Analyze relationship between stars and forks
-   Understand repository growth over time

------------------------------------------------------------------------

## How to run

git clone
https://github.com/your-username/github-data-analysis-pipeline.git\
cd github-data-analysis-pipeline\
pip install pandas matplotlib requests\
jupyter notebook

------------------------------------------------------------------------

## Notes

-   GitHub API data is limited (pagination not handled)
-   Results are based on available sample data

