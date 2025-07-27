# Fun with Pandas

## Intro
Track transactions using the sms.db sqlite database extracted from an encrypted iphone backup using libimobiledevice.

Used pandas for extracting and formatting relevant information from the database into a csv file which was then imported into metabase for visualization.

Data was read into a dataframe using the pandas.read_sql_query function. Relevant piece of data like amount and sender/receiver was extracted using patterns found within the text body. The timestamp of the message was used as the timestamp of the transaction as there isn't a noticable delay between both.

## Metabase

Metabase was used for visualizing the extracted data. It's a simple visualization tool that supports data ingestion from csv files. 

## Visuals
[Bar Graph](./visuals/bar_graph.png)
