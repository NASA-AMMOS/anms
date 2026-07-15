This file will contain upgrading instructions for all future tagged releases.

# Upgrading v2.0.0 to main

Note: If data preservation in the postgresql database is not required, `podman volume rm anms_postgres-data` is the only step required to start with a clean database.

## Postgresql 14 to 18 upgrade

If you wish to preserve existing data, you should backup the existing DB prior to updating then follow the Postgres upgrade guide. You can access the container with `podman|docker exec postgres bash`
https://www.postgresql.org/docs/current/pgupgrade.html

## Grafana DB Update
A new database named `grafana_internal_db` needs to be created in postgres. 

This can be done from the commandline or via the dev UI. 

In the latter case, ensure your instance is started with the `dev` and `full` profiles.  Go to Adminer (link provided in UI Help page) and either manually create the DB or 'Execute SQL' and upload the file `grafana/create_grafana_db.sql`

# Upgrading v1.x to v.2.0.0

It is recommended to start fresh (delete any existing ANMS-related containers and volumes) when transitioning from ANMS v1 to v2.

If you have data or customizations in a v1 installation that you need to migrate, please contact us or open an issue to discuss.

