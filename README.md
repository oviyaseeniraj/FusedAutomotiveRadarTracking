# mmSnap
Codebase for mmSnap: Bayesian One-Shot Fusion in a Self-Calibrated mmWave Radar Network (Accepted for publication at RadarConf 2025)

## Overview
Contains the codebase for the end-to-end mmSnap Pipeline containing the blocks for :

- [Range-Doppler-Angle Processing](#range-doppler-angle-processing)
- [Tracking](#tracking)
- [Self-Calibration](#self-calibration)
- [One-Shot Fusion](#one-shot-fusion)

### Range-Doppler-Angle Processing

- Input : 5D Radar Cube Data (Format : Frames X Chirps per Frame X Num_Rx X Num_Tx X ADC Samples)
- Output : (Range, Doppler, Angle) for detections
- Summary : The raw ADC data is converted from its original radar cube format 
into Range-Doppler-Angle point clouds for each frame by applying Fast Fourier Transforms (FFTs) 
along the relevant dimensions. To concentrate on moving targets, 
static clutter removal is conducted, followed by the application of a 
two-dimensional Ordered-Statistics Constant False Alarm Rate (2D OS-CFAR) 
detection across the frames for additional refinement.

### Tracking 

- Input : RDA Map
- Output : Detection Centroids and corresponding Tracks
- Summary : In the tracking stage, DBSCAN clustering extracts the centroids 
of point clouds, which are subsequently processed by an Extended Kalman Filter (EKF) 
for continuous tracking. For human targets within a distance of 10 meters, 
the point cloud exhibits significant Doppler variation due to limb movements. 
We have developed a variant of DBSCAN to extract a cluster center that 
represents the torso's position and motion. This approach enables the 
self-calibration and one-shot fusion algorithms, which are based on point 
target models, to remain straightforward and effective.

### Self-Calibration

- Input : Tracks from both radar perspectives
- Output : Relative Optimal Pose Estimates (Calibration)
-Summary : We integrate target tracking with pose estimation by “matching” 
each node’s observation of a common target in a least-squares sense, 
yielding a closed-form calibration solution. 

### One-Shot Fusion

- Input : Centroids from both Radar Perspectives, Calibration
- Output : Instantaneous Fused State and State Covariance estimates of targets
- Summary : We firstly match the centroids from both radar perspectives using 
the Hungarian Algorithm. Then we perform a Regularized Non-Linear Least Squares 
Optimization to obtain the Bayesian one-shot fused estimate using suitable 
priors for human motion.


## Link to Paper

Arxiv Link : [mmSnap](https://arxiv.org/abs/2505.00857)