docker run \
  -p 5000:5000 \
  -e "AUTOAPI_NAME=$AUTOAPI_NAME" \
  -e "AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID" \
  -e "AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY" \
  -e "AUTOAPI_BUCKET=$AUTOAPI_BUCKET" \
  -v `pwd`/data_sources:/data_sources \
  --rm -it 18fgsa/autoapi "$@"
