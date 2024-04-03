# Define a docker compose project.
# The title of this resource is the project name.
#
# @param ensure The desired state of the project, if 'present' the containers are started each time puppet is run.
# @param compose_files The configuration files for this project.
# @param up_args Additional arguments for `docker compose ... up ...` command
#
define anms::docker_compose(
  Enum['present','absent'] $ensure,
  Array[String] $compose_files,
  String $up_args = '',
) {
  require anms::docker

  $files_args = join($compose_files, ' ')
  $is_running = "docker compose ls --filter \"name=${title}\" | tail --lines=+2 | grep running"

  case $ensure {
    'present': {
      exec { "docker-compose-${title}-up":
        path => $::path,
	command => "docker compose -p ${title} -f ${files_args} up --detach --remove-orphans ${up_args}",
      }
    }
    'absent': {
      exec { "docker-compose-${title}-up":
        path => $::path,
        command => "docker compose -p ${title} -f ${files_args} rm --force --stop",
	onlyif => $is_running,
      }
    }
  }
}