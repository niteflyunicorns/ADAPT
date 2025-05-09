# ADAPT
Anomaly Detection in Asteroid Patterns and Trends

## What is ADAPT?
ADAPT is a processing system that will be responsible for processing incoming streams of astronomical data from the Legacy Survey of Space and Time (LSST) at the Vera C. Rubin Observatory in Chile, filtering out individual asteroids whose behavior appears to be deviating from their normal behavior. The goal is for ADAPT to detect early warning signs for changes to an asteroid’s behavior and send alerts to the astronomy community in advance so that astronomers can potentially observe these changes as they are happening.

## How does it work?
Currently, we are in the process of figuring out what the early warning signs are and what the best algorithm (or combination of algorithms) is to detect these signs. This research is ongoing, and we are always welcoming new contributors. ADAPT currently features the following pipeline:

### DBSCAN:
Density-Based Spatial Clustering Applications with Noise (DBSCAN) is an unsupervised machine learning algorithm that clusters points based on proximity `eps` and density `min_pts`. Our pipeline utlizes DBSCAN through Python's scikit-learn as the first layer of filtering. Currently, we use a static 
```
eps = 0.04
min_pts = 3
```
for every asteroid in the database. We chose this because in our parameter tuning tests, it performed well on multiple asteroids, giving a good balance between the noise level and the number of clusters. 

### Isolation Forest:
Separate from the DBSCAN filtering, we also run the data through Isolation Forest. Isolation Forest (also available though Python's scikit-learn package) is another unsupervised machine learning algorithm. Instead of clustering points together, Isolation Forest randomly and recursively splits the data, calculating the number of splits needed to isolate a point from the rest of the data. Points with less splits needed are labeled as 'anomalies'. Currently, the only parameter we give our Isolation Forest model is the `random_state` parameter, which ensures we can reproduce results.

### Hybrid & Post Processing:
After running both DBSCAN and Isolation Forest on the data, we combine the results of both algorithms in the following manner.
* Ignore `noise` and largest clusters from DBSCAN.
* Cross-reference clusters from DBSCAN against the `anomaly` points from Isolation Forest.
    * Any clusters with <50% of their points flagged by Isolation Forest get ignored.
* Any asteroids with <2 clusters meeting the above criteria are also ignored.

The result is a significantly smaller list of potentially interesting asteroids that we can manually inspect and recommend to the general public for follow-up observation. We currently reduce the dataset down to 42.19% of the original size, but we aim to reduce further so that we have a more focused result set. Our ongoing research is working on achieving this.

## Using ADAPT

Please visit our [User Manual]() for more information on setting up and using the ADAPT program.

## Contributing

We are always welcoming contributions from the community. If you are interested in contributing to the ADAPT project, please visit our [Contributing](/docs/CONTRIBUTING.md) docs for more information.

## Images

## More Information
This repository is maintained and managed by Savannah Chappus (aka. [niteflyunicorns](<https://github.com/niteflyunicorns>)).
For more information and work in this area, please visit [SNAPS](https://rc.nau.edu/snaps/).

**Other related resources:**

[LSST & Rubin Observatory](<https://rubinobservatory.org/>)

[ZTF](<https://www.ztf.caltech.edu/index.html>)