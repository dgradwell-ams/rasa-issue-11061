#!/usr/bin/env bash

curl 'http://localhost:5005/webhooks/session_test/webhook' \
  -X 'POST' \
  -H 'content-type: application/json' \
  --data-raw '{"sender":"78e07430-1c30-415a-8e7c-f9d84a16faf7","text":"hello","metadata":{"foo":"bar"}}'