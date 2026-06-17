.PHONY: doctor validate-schema

doctor:
	@./scripts/doctor.sh

validate-schema:
	@sqlite3 :memory: < schema/create_tables.sql
	@echo "Schema SQL validated."
