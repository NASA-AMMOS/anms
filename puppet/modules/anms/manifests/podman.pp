# Install podman and podman-compose according to upstream procedures at
# https://docs.podman.io/en/latest/markdown/podman-compose.1.html
#
class anms::podman() {
  case $facts['os']['family'] {
    'RedHat':  {
      package { ['docker-ce', 'docker-ce-cli', 'containerd.io', 'docker-buildx-plugin', 'docker-compose-plugin']:
        ensure => 'absent',
        before => [Package['podman'], Package['podman-compose']],
      }
      package { 'yum-utils':
        ensure => 'installed',
      }
      file { '/etc/yum.repos.d/docker.repo':
        ensure => 'absent',
      }
      exec { 'yum-repo-docker-ce':
        path    => $facts['path'],
        command => 'yum-config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo',
        creates => '/etc/yum.repos.d/docker-ce.repo',
        require => Package['yum-utils'],
        before  => [Package['docker-ce'], Package['docker-buildx-plugin'], Package['docker-compose-plugin']],
      }
    }
    default: {}
  }

  package { ['podman', 'podman-compose', 'container-tools']:
    ensure => 'installed',
  }

  file { '/etc/containers/containers.conf':
    source  => 'puppet:///modules/anms/containers.conf',
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    require => Package['podman'],
  }
  file { '/etc/containers/nodocker':
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    require => Package['podman'],
  }

  # systemd service to load compose configs as pods
  systemd::unit_file { 'podman-compose@.service':
    source => 'puppet:///modules/anms/podman-compose@.service',
  }
  file { '/etc/containers/compose':
    ensure  => 'directory',
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    require => Package['podman'],
  }
  file { '/etc/containers/compose/projects':
    ensure  => 'directory',
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    require => Package['podman'],
  }
}
