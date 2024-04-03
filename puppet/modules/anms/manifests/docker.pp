# Install docker and docker-compose according to upstream procedures at
# https://docs.docker.com/engine/install/rhel/#set-up-the-repository
# https://docs.docker.com/engine/install/rhel/#install-docker-engine
#
class anms::docker() {
  case $facts['os']['family'] {
    'RedHat':  {
      package { ['podman', 'runc']:
        ensure => 'absent',
        before => Package['docker-ce'],
      }
    }
    default: {}
  }

  package { 'yum-utils':
    ensure  => 'installed',
  }
  file { '/etc/yum.repos.d/docker.repo':
    ensure => 'absent',
  }
  exec { 'yum-repo-docker-ce':
    path    => $facts['path'],
    command => 'yum-config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo',
    creates => '/etc/yum.repos.d/docker-ce.repo',
  }
  package { ['docker-ce', 'docker-ce-cli', 'containerd.io', 'docker-buildx-plugin', 'docker-compose-plugin']:
    require => Exec['yum-repo-docker-ce'],
  }
  service { 'docker':
    require => Package['docker-ce'],
  }

  file { '/usr/local/bin/docker-compose':
    ensure => 'absent',
  }
  file { '/etc/docker/daemon.json':
    source => 'puppet:///modules/anms/docker-daemon.json',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
    notify => Service['docker'],
  }
}