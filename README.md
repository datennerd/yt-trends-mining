# YouTube Trends Mining

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub Super-Linter](https://github.com/datennerd/yt-trends-mining/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)
[![GitHub watchers](https://img.shields.io/github/watchers/datennerd/yt-trends-mining?style=social)](https://github.com/datennerd/yt-trends-mining)
[![GitHub forks](https://img.shields.io/github/forks/datennerd/yt-trends-mining?style=social)](https://github.com/datennerd/yt-trends-mining)
[![GitHub Repo stars](https://img.shields.io/github/stars/datennerd/yt-trends-mining?style=social)](https://github.com/datennerd/yt-trends-mining)

This script runs daily as a [GitHub Action](https://docs.github.com/en/actions) and uses the [YouTube Data API](https://developers.google.com/youtube/v3) to store various video and channel information as a CSV file for all recent videos on a country's [YouTube Trends](https://www.youtube.com/feed/trending) page in a [Google Cloud Storage](https://cloud.google.com/storage) bucket.

![Banner](banner.png)

## Exploratory Data Analysis

In [notebooks/eda.ipynb](https://github.com/datennerd/yt-trends-mining/blob/main/notebooks/eda.ipynb) you can see the results of the analysis for the period from 01.02.2021 to 17.03.2023 with almost 386.000 rows of data from 7800 csvs *(as of 26.03.2023)*.
This notebook can currently only run locally and requires a credentials.json file from Google Cloud Platform to access the Google Cloud Storage Bucket.
All CSV files are then downloaded and stored in a country-specific subfolder for analysis. An example CSV can be found in the notebooks folder.
