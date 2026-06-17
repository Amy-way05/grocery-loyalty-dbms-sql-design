#!/usr/bin/env sh
set -eu

required_files="
README.md
LICENSE
Makefile
schema/create_tables.sql
schema/original_schema_notes.md
queries/loyalty_analysis.sql
queries/store_performance_analysis.sql
queries/reward_strategy_analysis.sql
queries/customer_review_analysis.sql
docs/project-summary.md
docs/methodology.md
docs/data-dictionary.md
outputs/executive-insights.md
assets/erd.md
database/README.md
reports/README.md
"

missing=0

printf "Repository health check\n"
printf "=======================\n"

for file in $required_files; do
  if [ -f "$file" ]; then
    printf "ok   %s\n" "$file"
  else
    printf "miss %s\n" "$file"
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  printf "\nHealth check failed: required files are missing.\n"
  exit 1
fi

sqlite3 :memory: < schema/create_tables.sql

printf "\nAll essentials are present and schema SQL is valid.\n"
