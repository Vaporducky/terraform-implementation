#!bin/bash

# Install python virtual environment

# VARIABLE DEFINITION
# ===============================================================
TF_PATH="./architecture/Terraform/"
CLASS_STORAGE="Standard"
REGION="us-central1"
# Create a bucket for the backend
BUCKET="gs://${DEVSHELL_PROJECT_ID}-tf-backend"

# Set Project ID where necessary
for file in ${TF_PATH}/*/**; do
    sed -i "s/<PROJECT_ID>/${DEVSHELL_PROJECT_ID}/g" "$file"
done
# ===============================================================

# ===============================================================
# CLOUD STORAGE
# Create bucket
gsutil mb -c "${CLASS_STORAGE}" \
-l "${REGION}" \
${BUCKET}
# Set versioning in case of recovery disaster
gsutil versioning set 'on' ${BUCKET}
# ===============================================================

# Export Environment variables
export PROJECT_ID=${DEVSHELL_PROJECT_ID}
export TOPIC_ID="bicycle_analytics_report_parameters"
export SUBSCRIPTION_ID="bicycle-analytics-dataflow-trigger"
export SA_CF_PARAMETER_PUBLISHER="cf-publish-parameters-bicycle@${PROJECT_ID}.iam.gserviceaccount.com"
export COMPOSER_VARIABLES="./architecture/Composer/composer_variables.json"

# CLOUD STORAGE
gcloud storage buckets create "gs://${PROJECT_ID}-ingestion" \
 --project=${PROJECT_ID} \
 --default-storage-class=STANDARD \
 --location=us-central1 \
 --uniform-bucket-level-access

# PUB/SUB
# Create schema
gcloud pubsub schemas create "${TOPIC_ID}_schema" \
    --type='avro' \
    --definition-file="./architecture/PubSub/Schema/${TOPIC_ID}_schema.json"
# Create topic
gcloud pubsub topics create "${TOPIC_ID}" \
    --message-encoding=JSON \
    --schema="${TOPIC_ID}_schema"

gcloud pubsub subscriptions create "${SUBSCRIPTION_ID}" \
    --topic="${TOPIC_ID}" \
    --enable-message-ordering \
    --expiration-period="never" \
    --message-retention-duration="10h" \
    --ack-deadline=60

# CLOUD FUNCTIONS
cd "./src/cloud-functions/parameter_publisher/"
gcloud functions deploy publish_parameters \
    --runtime python310 \
    --trigger-http \
    --no-allow-unauthenticated \
    --service-account="${SA_CF_PARAMETER_PUBLISHER}"
export BICYCLE_ANALYTICS_PUBLISH_PARAMETERS_URL=$(gcloud functions describe publish_parameters | grep 'url:' | sed 's/url://g')
cd "../../../"

# COMPOSER
# Create variable file
echo '{' > ${COMPOSER_VARIABLES}
echo -e "\t\"PROJECT_ID_secret\": \"${PROJECT_ID}\"," >> ${COMPOSER_VARIABLES}
echo -e "\t\"TOPIC_ID\": \"${TOPIC_ID}\"," >> ${COMPOSER_VARIABLES}
echo -e "\t\"SUBSCRIPTION_ID\": \"${SUBSCRIPTION_ID}\"" >> ${COMPOSER_VARIABLES}
echo '}' >> ${COMPOSER_VARIABLES}

# ==============================================================================
# Set composer environment variable
# gcloud composer environments update \
# my-composer \
#  --location us-central1 \
#  --update-env-variables=TOPIC_ID=${TOPIC_ID}
# gcloud composer environments update \
#   my-composer \
#   --location us-central1 \
#   --update-env-variables=SUBSCRIPTION_ID=${SUBSCRIPTION_ID}
# 
# gcloud composer environments describe my-composer \
#   --location us-central1 \
#   --format="value(config.softwareConfig.pypiPackages)"
# 
# gcloud beta composer environments list-packages \
#     my-composer \
#     --location us-central1
# 
# gcloud composer environments update my-composer \
#     --location us-central1 \
#     --update-pypi-packages-from-file "./architecture/Composer/requirements.txt"
# ==============================================================================


# BIGQUERY
# Create datasets
bq --location=US mk -d bicycle_dataset
bq --location=US mk -d bicycle_analytic

# Replace project in SQL create statements
sed -i -E "s/project/${PROJECT_ID}/" ./architecture/BigQuery/create_bike_trips_fact.sql
sed -i -E "s/project/${PROJECT_ID}/" ./architecture/BigQuery/create_on_demand_table.sql
sed -i -E "s/project/${PROJECT_ID}/" ./architecture/BigQuery/random_data.sql

bq mk --table \
    --schema "./architecture/BigQuery/quarter-cost-dim-table-schema.json" \
    --time_partitioning_field quarter \
    --time_partitioning_type DAY \
    ${PROJECT_ID}:bicycle_dataset.quarter_cost_dim