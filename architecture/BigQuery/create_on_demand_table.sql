CREATE TABLE `project.bicycle_analytic.on_demand_report`
PARTITION BY DATE_TRUNC(start_time, DAY)
CLUSTER BY bike_id, start_station_name, end_station_name
AS
SELECT
      duration_minutes,
      ROUND(duration_minutes * 0.6, 2) AS trip_cost,
      bikeid AS bike_id,
      start_time,
      TIMESTAMP_ADD(start_time, INTERVAL duration_minutes MINUTE) AS end_time,
      start_station_id,
      start_station_name,
      end_station_id,
      end_station_name
FROM
  `bigquery-public-data.austin_bikeshare.bikeshare_trips`
LIMIT 0