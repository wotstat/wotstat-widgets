#!/bin/bash

CACHE_CONTROL='max-age=31536000'
S3_BUCKET_URL="s3://cef-storage.wotstat.info"
ENDPOINT_URL="https://storage.yandexcloud.net/"

aws --endpoint-url="$ENDPOINT_URL" \
  s3 cp . "$S3_BUCKET_URL" \
  --recursive \
  --exclude "*" \
  --include "wotstat.widgets.cef.*.zip" \
  --cache-control "$CACHE_CONTROL" \
  --profile wotstat