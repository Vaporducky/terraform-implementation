# Description

This is a small project regarding the architecture of small company: **"Bikeshare Enterprise"**.

Given a range of dates (*e.g.* `initial_day=2021-01-01`, `end_day=2022-01-02`), the goal is to determine the total cost for each trip.

$t * T_{C} *$

where
- $T_{C}$ is the trip cost per minute
- $t$ is the duration of the trip in minutes

### Workflow
1. A Cloud Function publishes a message (ingested through HTTPS) in a PubSub topic
2. A Cloud Function is triggered when a message is Published in the topic
3. DataFlow **batch** job is submitted through the previous Cloud Function
4. Data is load/truncated into a BQ table 

### Terraform
Adding *Terraform* to manage Cloud Infrastructure.

## Initial Configuration
Run `setup.sh` in order to configure the project. This script will set the project ID in various scripts.