#!/usr/bin/env bash
export ZD_BASE_URL="https://*.zendesk.com"
export ZD_USER=""
export ZD_PWD=""
export SQLALCHEMY_CONN_STRING="postgresql://user:password@localhost/database"

python zd-hc-api-export.py