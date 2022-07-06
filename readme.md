# Stay point identification based on the correlation coefficient

## Prerequisite.
After the courier has properly delivered the courier, he needs to confirm the proper delivery through the handheld PDA, which will upload the current coordinates and the proper delivery mark.

Through the GPS location and time recorded by the courier's handheld PDA, the location of the area where the courier stays longer in the process of collection and delivery is obtained through the algorithm. Then according to the courier order information, query the user to fill in the order address and coordinates. Comparing the stopping point with the next order address, the following applications can be made.


  1. to determine whether the courier has false proper delivery. Some couriers will upload the information together after the unified proper delivery. By comparing the dwell point and confirming the uploading of proper delivery information, we can determine whether the courier has uploaded according to the specification. 2.

  2. In addition, according to the excavated stopping point information, combined with the text recognition and similarity judgment of the order address filled by the user, the proper delivery point of the order address can be categorized to save the courier's time.

  3. Later, more effective information about geographic location or cell area can be mined based on the location of dwell points.

## Implementation steps.

1. extract the PDA upload data of eight couriers across the country throughout the day on 2018-11-12. Data attributes are courier id, date and time (accurate to the second), latitude, longitude (latitude and longitude coordinates are in WGS84 format)

2. processing format, remove redundant content, separated by tabs or commas

3. use the dictionary sub-id to save the courier information, the list to save the courier point set, the tuple to save the time and latitude and longitude of a single point of the record

4. convert the 2018-11-12 H:M:S format to timestamp and save the point set in each courier in chronological order

5. calculate the current timestamp and the previous timestamp distance to check that the average speed is unevenly distributed and there is a lot of noise (the following figure shows the time series of the average speed of a courier on that day)
![X-axis timestamp Unit: second, Y-axis average speed Unit: m/s](p1.png 'p1')

Plot on the map.

![X-axis Timestamp in seconds, Y-axis Average velocity in meters/second](p2.png 'p2')

Therefore, it is not possible to use the current data to analyze the dwell points, so data cleaning is required.

6. Cleaning data
   1. The set of list points sorted by timestamp for each courier in the dictionary is processed, and if the distance between the current point and the point before the timestamp exceeds the time threshold, the two points are saved separately, otherwise these two points are saved in the same list. By this method, a timestamp-ordered list is partitioned into multiple sets of lists that are partitioned by distance again.

2. Process the partitioned list collection to find the noise points in it. Create a new list and process each of the separated sublists. Put the first point in the sub-list into the new list, and then traverse the sub-list. If the distance between the current point and the last point in the new list is less than the distance threshold and the velocity threshold, the point is judged not to be a noise point, and the point is put into the new list. If it is a noise point, the next point is traversed and the point is discarded. If the total number of points in the new list does not exceed the point threshold, the list is discarded. Finally, the integrated multiple new lists are saved in a single total list, and the total list is saved again in the dictionary. The default time threshold is 600 seconds, the distance threshold is 2000 meters, the speed threshold is 20 meters/second, and the point threshold is 5. 3.

3. Separate the new list by time threshold again, in terms of time and distance. If the distance between the current point and the previous point is greater than the distance threshold, or the time is greater than the time threshold, the separation will be made. The distance threshold is 500 meters and the time threshold is 2400 seconds.

After data cleaning, a road map is drawn, which shows the path of multiple segments traveling along the road in an orderly manner.

![X-axis Timestamp Unit: second, Y-axis Average speed Unit: m/s](p3.png 'p3')

7. After data cleaning, choose the correlation algorithm to calculate the dwell points.
Read the paper "Algorithm of trajectory dwell point recognition based on correlation coefficient" and find the scenario is more suitable.

The more traditional method is the recognition algorithm based on distance and time thresholds according to the distance and time characteristics of the trajectory dwell points. In the dwell point study, the velocity attributes of the trajectory points are also separated out. In many literatures, the trajectory points with lower velocity will be referred to as stationary points, and the duration at the stationary point is used as an important basis for identifying the dwell points.
There is another research direction of trajectory dwell point analysis, which is density-based methods for trajectory dwell point identification. This kind of dynamic method is built on the basis of existing classical clustering methods (k-median algorithm, etc.).

Algorithm of trajectory stay point identification based on correlation coefficient: by calculating each point in the trajectory can calculate the correlation coefficient according to the coordinates of the neighboring points, the smaller the absolute value of the correlation coefficient, the relatively larger the change of travel direction near the neighboring points.
- Calculating the absolute value of the correlation coefficient of the trajectory points by the coordinates of the trajectory in turn.

- Filtering the trajectory points, if the absolute value of correlation coefficient of the trajectory points is less than the Min value, the point is recognized as a key point.

- Arrange these key points in chronological order to form a sequence of key points.

- Generally, the points in the trajectory points for sequential key point filtering only leave the points with large direction change compared with the neighboring points, but the number is still high and the points near the turn are likely to be kept, which affects the further judgment of the stay point, so it is necessary to filter the key point sequence again. In the second filtering process, we use the key point sequence identified for the first time as the original trajectory sequence, still based on the correlation coefficient of the relevant points for over
In the second filtering process, we use the first identified key point sequence as the original trajectory sequence, and still filter it according to the correlation coefficient of related points, and arrange the generated points in time order to form the second key point sequence.

![X-axis Timestamp Unit: sec, Y-axis Average velocity Unit: m/s](p4.png 'p4')

You can see that there are two types of points on the way. The light blue color is the set of route track points after removing the noise. The dark blue points are the key points. The key points are the points with large changes in direction, and the dwell points can be obtained by processing the key points and the surrounding points.
In the calculation process, the x and y values are the latitude and longitude values respectively.

8. The adjacent key points are divided, and if the distance exceeds the threshold, the sequence of key points is divided at these two points.

9. Stopping point identification
1. Calculate the minimum enclosing circle of this key point region, read the literature "Analysis and improvement of minimum enclosing circle algorithm for discrete point set", and try the related algorithm.
2. find the relevant points in and near this circle along the direction of the lower and upper time limits of the key point region respectively, and find the upper and lower time limits of the trajectory in the relevant region of this key point.
3. extract the points between the identified lower and upper time limits to form the key point related region.


The extraction of dwell points is mainly divided into two stages: key point region division and dwell point identification. In the experiment, according to the analysis of trajectory data in the trajectory, the correlation coefficient (Pearson coefficient) threshold is set to 0.55, the key point division threshold is set to 75 meters, the ratio of trajectory length to area radius for dwell point identification is set to 1, and the dwell time is at least 120 seconds. The following figure shows the recognition results of the example trajectory.

![X-axis Time stamp Unit: second, Y-axis Average speed Unit: m/s](p5.png 'p5')

(The newly added red point is the dwell point)

# Experimental statistics

Last week, using the method of calculating dwell points by average speed, the number of dwell points is basically proportional to the change of threshold value
! [X-axis Time stamp Unit: second, Y-axis Average speed Unit: m/s](p6.png 'p6')

Dwell areas are calculated using the correlation coefficient method to aggregate multiple points with a single area.

 ![X-axis Timestamp Unit: sec, Y-axis Average velocity Unit: m/s](p7.png 'p7')

After the ratio of radius to distance sum is higher than 2, the dwell point area cannot be calculated. The three lines above are the stay thresholds of the courier after getting the dwell point, which are 30 seconds, 60 seconds and 120 seconds, respectively.

![X-axis Timestamp Unit: sec, Y-axis Average velocity Unit: m/s](p8.png 'p8')

After the correlation coefficient threshold exceeds 0.65 (i.e., when a high correlation is required), the obtained dwell point rises steeply.



