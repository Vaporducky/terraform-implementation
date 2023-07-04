CREATE TABLE `project.bicycle_dataset.bike_trips_fact`
PARTITION BY DATE_TRUNC(start_time, DAY)
AS
SELECT * FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`