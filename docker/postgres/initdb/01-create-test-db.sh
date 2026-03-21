#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
SELECT 'CREATE DATABASE test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test_db')\gexec
EOSQL
