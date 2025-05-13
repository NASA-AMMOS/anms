# The root class for installing the ANMS
#
class anms(
  String $ctr_image_prefix,
  String $ctr_image_tag,
  String $version = '',
  String $gw_fqdn = $facts['networking']['fqdn'],
  Optional[String] $ctr_registry_user = undef,
  Optional[String] $ctr_registry_pass = undef,
  String $cam_server_url = '',
  String $cam_admin_user = 'amAdmin',
  String $cam_admin_password = '',
  String $cam_agent_name = $facts['networking']['fqdn'],
  String $cam_agent_password = '',
  Optional[String] $tls_server_key = undef,
  Optional[String] $tls_server_cert = undef,
  Optional[String] $tls_server_ca = undef,
  Boolean $use_testenv = false,
) {
  require Class['anms::hostenv']

  file { ['/ammos', '/ammos/anms']:
    ensure => 'directory'
  }
  file { '/ammos/anms/.env':
    ensure  => 'file',
    content => epp('anms/env.epp'),
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
  }
  file { ['/ammos/etc', '/ammos/etc/pki', '/ammos/etc/pki/tls',
          '/ammos/etc/pki/tls/private', '/ammos/etc/pki/tls/certs']:
    ensure => 'directory'
  }
  file { '/ammos/etc/pki/tls/private/ammos-server-key.pem':
    ensure => 'file',
    source => $tls_server_key,
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }
  file { '/ammos/etc/pki/tls/certs/ammos-server-cert.pem':
    ensure => 'file',
    source => $tls_server_cert,
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }
  file { '/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt':
    ensure => 'file',
    source => $tls_server_ca,
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }

  case $facts['os']['family'] {
    'RedHat':  {
      # SELinux modules for each container
      $containers = [
        'adminer',
        'anms-core',
        'anms-ui',
        'aricodec',
        'authnz',
        'grafana',
        'grafana-image-renderer',
        'amp-manager',
        'mqtt-broker',
        'nginx',
        'opensearch',
        'opensearch-dashboards',
        'postgres',
        'redis',
        'transcoder',
      ]
      anms::semodule_cil { 'anms-ports':
        source_cil => 'puppet:///modules/anms/selinux/anms-ports.cil',
        require    => Package['udica'],
        before     => Anms::Compose['anms'],
        notify     => Anms::Compose['anms'],
      }
      $containers.each |$ctrname| {
        anms::semodule_cil { $ctrname:
          source_cil => "puppet:///modules/anms/selinux/${ctrname}.cil",
          extra_cil  => [
            '/usr/share/udica/templates/base_container.cil',
            '/usr/share/udica/templates/net_container.cil',
          ],
          require    => [
            Package['udica'],
            Anms::Semodule_cil['anms-ports'],
          ],
          before     => Anms::Compose['anms'],
          notify     => Anms::Compose['anms'],
        }
      }
    }
    default: {
    }
  }

  # Images pulled from remote registry
  if !empty($ctr_image_prefix) and !empty($ctr_registry_user) and !empty($ctr_registry_pass) {
    exec { 'image-repo-login':
      path    => $facts['path'],
      command => "podman login ${ctr_image_prefix} --username \"${ctr_registry_user}\" --password \"${ctr_registry_pass}\"",
      before  => [
        Anms::Compose['anms'],
        Anms::Compose['testenv'],
      ],
    }
  }

  # volume for TLS-related PKIX files
  file { '/ammos/anms/create_volume.sh':
    ensure => 'file',
    source => 'puppet:///modules/anms/create_volume.sh',
    owner  => 'root',
    group  => 'root',
    mode   => '0755',
  }
  exec { 'volume-ammos-tls':
    path      => $facts['path'],
    command   => '/ammos/anms/create_volume.sh',
    unless    => 'podman volume inspect ammos-tls',
    require   => [
      File['/ammos/anms/create_volume.sh'],
    ],
    subscribe => [
      File['/ammos/etc/pki/tls/private/ammos-server-key.pem'],
      File['/ammos/etc/pki/tls/certs/ammos-server-cert.pem'],
      File['/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt'],
    ],
    before    => Anms::Compose['anms'],
    notify    => Anms::Compose['anms'],
  }

  file { '/ammos/anms/anms-compose.yml':
    ensure => 'file',
    source => 'puppet:///modules/anms/docker-compose.yml',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }
  anms::compose { 'anms':
    ensure       => 'present',
    directory    => '/ammos/anms',
    compose_file => 'anms-compose.yml',
    subscribe    => [
      File['/ammos/anms/anms-compose.yml'],
      File['/ammos/anms/.env'],
    ],
  }

  if $use_testenv {
    file { '/ammos/anms/testenv-compose.yml':
      ensure => 'file',
      source => 'puppet:///modules/anms/testenv-compose.yml',
      owner  => 'root',
      group  => 'root',
      mode   => '0644',
    }
    anms::compose { 'testenv':
      ensure       => 'present',
      directory    => '/ammos/anms',
      compose_file => 'testenv-compose.yml',
      require      => [
        Anms::Compose['anms'], # for the anms network
      ],
      subscribe    => [
        File['/ammos/anms/testenv-compose.yml'],
        File['/ammos/anms/.env'],
      ],
    }
  }
  else {
    file { '/ammos/anms/testenv-compose.yml':
      ensure => 'absent',
    }
    anms::compose { 'testenv':
      ensure       => 'absent',
      directory    => '/ammos/anms',
      compose_file => 'testenv-compose.yml',
    }
  }
}
