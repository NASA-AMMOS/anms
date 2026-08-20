This file will contain upgrading instructions for all future tagged releases.

# Upgrading v2.0.0 to v3.0.0

Data preservation is not currently supported and it is recommended to reset the database with  `podman volume rm anms_postgres-data` if not starting with a clean system.

If you have a need to preserve ANMS data during upgrade, please reach out to the dev team or submit a feature request to discuss.


# Upgrading v1.x to v.2.0.0

It is recommended to start fresh (delete any existing ANMS-related containers and volumes) when transitioning from ANMS v1 to v2.

If you have data or customizations in a v1 installation that you need to migrate, please contact us or open an issue to discuss.

