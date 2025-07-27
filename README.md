# Fun with Pandas

## Intro
Track transactions using the sms.db SQLite database extracted from an encrypted iPhone backup using libimobiledevice.

Used Pandas to extract and format relevant information from the database into a CSV file, which was then imported into Metabase for visualization.

Data was read into a DataFrame using the pandas.read_sql_query function. Relevant pieces of data—such as the amount and sender/receiver—were extracted using patterns found within the text body. The timestamp of the message was used as the timestamp of the transaction, as there isn’t a noticeable delay between the message and the actual transaction.

## Metabase

Metabase was used to visualize the extracted data. It's a simple visualization tool that supports data ingestion from CSV files.

## Visuals

### Bar Graph
![bar graph](./visuals/bar_graph.png 'bar graph')

### Pie Chart
![pie chart](./visuals/pie_chart.png 'pie chart')

