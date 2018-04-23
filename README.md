* NYSERDA SOLAR SCRAPE *

** About **

This project provides a script that downloads solar energy facility output data from the NYSERDA Distributed Generation site.

*** Installation and Usage ***
```
pip install lxml requests
python scrape.py
```

** Thought Process **

*** Planning ***

As always, the first step is to evaluate what the requirements of the task are. In this case, this only involved asking for some clarification on the scope of the project. The important points can be summarized as follows:

 * The software only needs to collect data, no processing is required beyond what it needed to store it.
 * The data should be kept as up to date as possible, both in terms of what stations are tracked and in terms of what data is available for each station.
 * All data that could be used to predict output should be gathered.

With that done, the next step is to investigate what solutions are available, and the benefits and drawbacks of each. The most immediately obvious solution was to use the predefined queries to pull data every week. This would solve the problem of needing to look for new locations, and be both the fastest and technically most simple. It would only get new data every week, but this should be acceptable for training purposes, since many stations only update their data weekly. This solution would also avoid scraping (programatically reading) the site, which is generally preferable. Unfortunately, these queries were discontinued last year, so this option falls through.

Another possibility that was considered is generating one report for all facilities each day. Although the site is made in such a way that scraping is unavoidable, this method would have minimized the number of requests made. However, the report fails to generate if more than about a fifth of the facilities are included, and when it does work it only includes the total output of the specified facilities, and their average ambient temperature.

This leaves only one solution: generating a report for each solar facility every day. This gives the most up to date possible information on each facility, and still requires only a few hundred requests.

*** Design ***

Next, an algorithm must be designed to implement the chosen solution. The first part of this process is to see what schema is needed to store the information available. In terms of SQL, two tables are needed. One to store information about each facility, and another to store the hourly data about each facility. The schema for the tables should look as follows:

facilities                                  output_logs
+------+------------+---------+--------+    +------+------+--------+----------------+-------------+---------------------+-------------+
| name | nyserda_id | address | active |    | date | time | output | output_quality | temperature | temperature_quality | facility_id |
+------+------------+---------+--------+    +------+------+--------+----------------+-------------+---------------------+-------------+

The schema for output_logs is simple enough, storing each line from each of the downloaded logs along with which facility that log is associated with. Although the model used for prediction will likely not use data that fails to pass relational checks, all data is kept. The schema for facility information includes the id of the facility on the NYSERDA site, whether or not the facility is current tracked according to said site, and other identifying information.

The general structure of the project is very simple. Using a scheduler, for example cron, a script is run each day. This script checks the list for any new facilities, which are added to the facilities table and marked as active. It then calculates the date range it needs to download for each facility based on when the last data recieved for that facility was and tries to download it. For newly added facilities, all available data is downloaded instead. If successful, that data is added to the output_logs table. Otherwise, that data is assumed to be still unavailable, and the error is ignored. Lastly, the script checks to see of any facilities are no longer marked as currently tracked, at which point they are marked as inactive in the database.

*** Implementation Details ***

Because of the simple nature of the script, and because performance isn't an issue, Python was chosen to minimize development time. This script is only a proof of concept and will download data for only one facility, although the code for discovering new facilities and updating old ones is mostly there. Additionally, code for communicating with the database is omitted.

*** Caveats ***

Because data doesn't seem to be retroactively corrected if it was of poor quality, this algorithm should gather all available data. It has a relatively slow runtime, but because it only needs to run once a day, this is not a problem. However, because it relies on scraping to get download links for the data, it will likely break when the interface for the site changes. Unfortunately, without a proper API, this is unavoidable.

