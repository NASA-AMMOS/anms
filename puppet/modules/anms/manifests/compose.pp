# Define a container compose project.
# The title of this resource is the project name.
#
# This uses the systemd service strategy discussed in
# https://www.redhat.com/en/blog/container-systemd-persist-reboot
# but for the entire compose project.
#
# @param ensure The desired state of the project, if 'present' the containers are started each time puppet is run.
# @param compose_files The configuration files for this project.
# @param pull_first If "compose ... pull" should be run before the service is activated
#
define anms::compose(
  Enum['present','absent'] $ensure,
  String $directory,
  String $compose_file,
  Boolean $pull_first = true,
) {
  require anms::podman

  case $ensure {
    'present': {
      if $pull_first {
        exec { "docker-compose-${title}-pull":
          path    => $facts['path'],
          command => "podman compose -p ${title} -f ${directory}/${compose_file} pull",
          require => [
            File["${directory}/${compose_file}"],
          ],
          before  => Service["podman-compose@${title}"],
        }
      }
      # Environment for podman-compose@.service instance
      file { "/etc/containers/compose/projects/${title}.env":
        ensure  => 'file',
        content => epp('anms/podman-compose-project.env.epp', {
          'title'        => $title,
          'directory'    => $directory,
          'compose_file' => $compose_file
        }),
        owner   => 'root',
        group   => 'root',
        mode    => '0644',
      }
      service { "podman-compose@${title}":
        enable  => true,
        require => [
          Systemd::Unit_file['podman-compose@.service'],
        ],
      }
    }
    'absent': {
      file { "/etc/containers/compose/projects/${title}.env":
        ensure => 'absent',
      }
      service { "podman-compose@${title}":
        enable  => false,
        require => [
          Systemd::Unit_file['podman-compose@.service'],
        ],
      }
    }
    default: {
      fail("Invalid ensure argument: ${ensure}")
    }
  }
}