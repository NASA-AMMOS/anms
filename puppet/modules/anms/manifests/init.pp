# The root class for installing the ANMS
#
class anms(
  String $docker_image_prefix,
  String $docker_image_tag,
  String $version = '',
  String $gw_fqdn = $facts['networking']['fqdn'],
  Optional[String] $docker_registry_user = undef,
  Optional[String] $docker_registry_pass = undef,
  String $cam_server_url = '',
  String $cam_admin_user = 'amAdmin',
  String $cam_admin_password = '',
  String $cam_agent_name = $facts['networking']['fqdn'],
  String $cam_agent_password = '',
  Optional[String] $tls_server_key = undef,
  Optional[String] $tls_server_cert = undef,
  Optional[String] $tls_server_ca = undef,
) {
  require Class['anms::hostenv']

  file { ['/ammos', '/ammos/anms']:
    ensure => 'directory'
  }
  file { '/ammos/anms/.env':
    ensure  => 'file',
    content => epp('anms/env.epp'),
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
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
        'ion-manager',
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
        before     => Anms::Docker_compose['anms'],
        notify     => Anms::Docker_compose['anms'],
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
          before     => Anms::Docker_compose['anms'],
          notify     => Anms::Docker_compose['anms'],
        }
      }
    }
    default: {
    }
  }

  # Images pulled from remote registry
  if !empty($docker_image_prefix) and !empty($docker_registry_user) and !empty($docker_registry_pass) {
    exec { 'docker-login':
      path    => $facts['path'],
      command => "docker login ${docker_image_prefix} --username \"${docker_registry_user}\" --password \"${docker_registry_pass}\"",
      require => Service['docker'],
      before  => [
        Anms::Docker_compose['anms'],
        Anms::Docker_compose['agents'],
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
    unless    => 'docker volume inspect ammos-tls',
    require   => [
      Service['docker'],
      File['/ammos/anms/create_volume.sh'],
    ],
    subscribe => [
      File['/ammos/etc/pki/tls/private/ammos-server-key.pem'],
      File['/ammos/etc/pki/tls/certs/ammos-server-cert.pem'],
      File['/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt'],
    ],
    before    => Anms::Docker_compose['anms'],
    notify    => Anms::Docker_compose['anms'],
  }

  file { '/ammos/anms/docker-compose.yml':
    ensure => 'file',
    source => 'puppet:///modules/anms/docker-compose.yml',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }
  anms::docker_compose { 'anms':
    ensure        => 'present',
    compose_files => ['/ammos/anms/docker-compose.yml'],
    up_args       => '--force-recreate',
    subscribe     => [
      File['/ammos/anms/docker-compose.yml'],
      File['/ammos/anms/.env'],
    ],
  }

  file { '/ammos/anms/agent-compose.yml':
    ensure => 'file',
    source => 'puppet:///modules/anms/agent-compose.yml',
    owner  => 'root',
    group  => 'root',
    mode   => '0644',
  }
  anms::docker_compose { 'agents':
    ensure        => 'present',
    compose_files => ['/ammos/anms/agent-compose.yml'],
    up_args       => '--force-recreate',
    require       => [
      Anms::Docker_compose['anms'], # for the anms network
    ],
    subscribe     => [
      File['/ammos/anms/agent-compose.yml'],
      File['/ammos/anms/.env'],
    ],
  }

  # Restart ducts to cache updated DNS resolution
  $ion_containers = [
    'ion-manager',
    'ion-agent2',
    'ion-agent3',
  ]
  $ion_containers.each |$ctrname| {
    exec { "restart-ducts-${ctrname}":
      command => "docker exec ${ctrname} ion_restart_ducts",
      path    => $facts['path'],
      require => [
        Anms::Docker_compose['anms'],
        Anms::Docker_compose['agents'],
      ],
    }
  }
}
