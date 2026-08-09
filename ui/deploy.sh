#!/bin/bash
set -e

set -a
source .env
set +a

BUCKET_NAME="fiohairstyles-crm-119376326150-us-east-1-an"
DISTRIBUTION_ID="ESTNV3W9I6N7K"
REGION="us-east-1"

npm run build

aws s3 sync out/ "s3://$BUCKET_NAME" --delete --region "$REGION"

aws cloudfront create-invalidation \
  --distribution-id "$DISTRIBUTION_ID" \
  --paths "/*"

echo "Deploy complete."
