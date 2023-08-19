There are five files containing the data displayed in the BITRE Congestion Report, three csv files and one geojson. The file containing route parameters can be found at the github repository at github.com/bitre-telematics/congestion.
The five files are:
route_metrics.csv: Containing summary data on each route, with the fields
  route_name - name of route in report
  min median travel time - the lowest median travel time (by hour) for the route
  max median travel time - the highest median traveltime (by hour) for the route
  Peak time to best ratio - The ratio of longest to shortest median time
  min iq travel time - the interquartile range width for the hour in which is was most narrow
  max iq travel time - the interquartile range width for the hour in which is was most wide
  Peak iq to best ratio - the ratio of the widest to most narrow iq ranges
  min median travel hour - the hour of day (from 0 to 23) when median travel times were least
  max median travel hour - the hour of day (from 0 to 23) when median travel times were greatest
  min iq travel hour - the hour of day for which the iq range was narrowest
  max iq travel hour - the hour of day for which the iq range was greatest
  total obvs - the number of vehicle observations used to calculate all time
  Mean excess time ratio - the arithmetic mean of the ratio, by hour, of travel times to the best travel time
  Mean excess time ratio - weighted - the arithmetic mean of the ratio, by hour, of travel times to the best travel time, weighted by observations in that   hour - hour of the day (from 0 to 23)
  Mean excess iq ratio - the arithmetic mean of the ratio, by hour, of iq ranges to the best iq range
  Mean excess iq ratio - weighted - the arithmetic mean of the ratio, by hour, of iq ranges to the best iq range, weighted by observations in that hour
  distance - the length of the route in metres

route_times.csv: Containing data for each hour, as graphed in the report, with the fields
  route_name - name of route
  hour - hour of the day (from 0 to 23)
  LQ_est - the travel time at the lowest quartile of speeds (that is the upper quartile of travel times) in seconds
  med_est - the travel time at the median travel speeds in seconds
  UQ_est - the travel time at the upper quartile of speeds (that is the lower quartile of travel times) in seconds
  LQ_est_char, med_est_char, UQ_est_char - the above but in human readable format
  n_obvs - the number of vehicle observations used to caculate the speeds for that hour

segment_summary.csv: containing summaries of the segments and their speeds used to calculate travel times
  route_name - the name of the route this data was generated for
  osm_id - an Open Street Map unqiue indentifier, valid at least at time of publication. A segment may appear in more than one route.
  hour - hour of day (from 0 to 23)
  n_obvs - the number of vehicle observations available for that hour and segment. This may be 0 in some cases in which case alternate methods were used to assume a distribution of speeds
  speed_limit - the speed limit. This report assumes all vehicles obey the speed limit. This was taken from OpenStreetMap where available and assumed based on road class and observed speed in others.
  UQ - the upper quartile of speed (kph)
  median - the median speed (kph)
  LQ - the lower quartile of speed (sph)
  distance - the distance traversed on this segment by the route - a segment may be used for different lengths on different routes

The file geometries.csv contains only whole route geometries. Individual segments can be obtained from OpenStreetMap.

city_wide_indices_2020.csv: contains index values for the 5 cities, indexed to year 2019
  mean_excess_time - the mean of the METR (as in route_metrics.csv) weighted by the product of total observations and the distance of the trip
  mean_uncert_odw - the mean of the MEUR (as in route_metrics.csv) weighted by the product of total observations and the distance of the trip
  mean_excess_time_odw_hw - the mean of the METR - weighted (as in route_metrics.csv) weighted by the product of total observations and the distance of the trip
  mean_uncert_odw_hw - the mean of the MEUR - weighted (as in route_metrics.csv) weighted by the product of total observations and the distance of the trip
  year - the year of the observation