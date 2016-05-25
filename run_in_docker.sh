#!/bin/sh
cd /autoapi
if [ -n "$AUTOAPI_BUCKET" ]; then
  invoke fetch_bucket
fi
invoke apify "/data_sources/**.*"
invoke serve
