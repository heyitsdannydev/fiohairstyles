#!/bin/bash
set -e

set -a
source .env
set +a

FUNCTION_NAME="fiohairstyles-crm-api"
REGION="us-east-1"

rm -rf build deploy.zip
mkdir build

uv export --no-dev --no-hashes -o requirements.txt

uv pip install --target build -r requirements.txt \
  --python-platform x86_64-manylinux2014 --python-version 3.13

cp -r app build/

cd build
zip -r ../deploy.zip . -x '*.pyc' -x '__pycache__/*'
cd ..

aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file "fileb://deploy.zip" \
  --region "$REGION"

echo "Deploy complete."