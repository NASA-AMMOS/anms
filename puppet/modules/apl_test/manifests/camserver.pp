# 
# This module relies on Yum repositories being configured on the target host
# prior to applying this module.
# 
# After all this run:
#  cd /ammos/cam-server/setup/data
#  sudo /ammos/cam-server/setup/bin/setup-cam-server.sh
#
class apl_test::camserver(
  Hash[String,String] $tls_ca_set = {
    'cam-ca' => 'puppet:///modules/apl_test/camserver/tls/certs/cam-ca.crt',
    'ipa-ca' => 'puppet:///modules/apl_test/camserver/tls/certs/ipa-ca.crt',
  },
  String $tls_server_cert = 'puppet:///modules/apl_test/camserver/tls/certs/ammos-server-cert.pem',
  String $tls_server_key = 'puppet:///modules/apl_test/camserver/tls/private/ammos-server-key.pem',
) {
  class { 'selinux':
    mode => 'permissive',
  }

  $cam_main_package = 'MGSS-ammos-asec-cam-server-cse-5.1.0-tomcat-9.0.62'
  ensure_packages(
    [
      'java-11-openjdk',
      'MGSS-ammos-asec-cam-config-store-5.1.0',
      'MGSS-ammos-asec-cam-server-5.1.0',
      'MGSS-ammos-asec-cam-server-cse-5.1.0',
      'MGSS-ammos-asec-cam-server-cse-5.1.0-json-sh-0.3.3',
      'MGSS-ammos-asec-cam-server-cse-5.1.0-tomcat-9.0.62',
      'MGSS-ammos-system-base-A31.1.camserver.1',
      'MGSS-ammos-system-current-A31.1.camserver.1',
    ],
    {
      ensure => 'present',
      require => Yumrepo['anms-deployment'],
    },
  )

  # turn on SSL debugging for the Tomcat install running CAM Server
  file { '/opt/ammos/cam-server/cse/5.1.0/tomcat9-9.0.62/bin/setenv.sh':
    content => 'JAVA_OPTS="-Djavax.net.debug=ssl,handshake"',
    owner   => 'root',
    group   => 'cam-adm',
    mode    => '0755',
    require => Package[$cam_main_package],
  }

  file { '/ammos/cam-server/setup/data/cam-config-params':
    content => epp('apl_test/camserver/cam-config-params.epp'),
    owner   => 'mgsscm',
    group   => 'cam-adm',
    mode    => '0640',
    require => Package[$cam_main_package], # for owner/group
  }
  file { '/ammos/cam-server/setup/data/passwords':
    content => epp('apl_test/camserver/passwords.epp'),
    owner   => 'mgsscm',
    group   => 'cam-adm',
    mode    => '0400',
    require => Package[$cam_main_package], # for owner/group
  }

  class { 'trusted_ca': }
  concat { '/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt':
    owner  => 'root',
    group  => 'ammos-tls',
    mode   => '0444',
    require => Package[$cam_main_package], # for owner/group
  }
  file { '/ammos/etc/pki/tls/certs/ammos-server-cert.pem':
    source => $tls_server_cert,
    owner  => 'cam-srv',
    group  => 'ammos-tls',
    mode   => '0444',
    require => Package[$cam_main_package], # for owner/group
  }
  file { '/ammos/etc/pki/tls/private/ammos-server-key.pem':
    source => $tls_server_key,
    owner  => 'cam-srv',
    group  => 'ammos-tls',
    mode   => '0400',
    require => Package[$cam_main_package], # for owner/group
  }
  openssl::export::pkcs12 { 'ammos-server-keystore':
    ensure   => 'present',
    basedir  => '/ammos/etc/pki/tls/private',
    pkey     => '/ammos/etc/pki/tls/private/ammos-server-key.pem',
    cert     => '/ammos/etc/pki/tls/certs/ammos-server-cert.pem',
    out_pass => 'changeit',
    require  => [
      File['/ammos/etc/pki/tls/certs/ammos-server-cert.pem'],
      File['/ammos/etc/pki/tls/private/ammos-server-key.pem'],
    ],
  }
  file { '/ammos/etc/pki/tls/private/ammos-server-keystore.p12':
    owner   => 'root',
    group   => 'ammos-tls',
    mode    => '0440',
    require => [
      Openssl::Export::Pkcs12['ammos-server-keystore'],
      Package[$cam_main_package], # for owner/group
    ],
  }

  $tls_ca_set.each |$key,$value| {
    # system root CA for openssl and java
    trusted_ca::ca { $key:
      source => $value,
    }

    # AMMOS-specific PEM chain
    concat::fragment { "ca-bundle-${key}":
      target => '/ammos/etc/pki/tls/certs/ammos-ca-bundle.crt',
      source => $value,
    }
    # AMMOS-specific java store
    trusted_ca::java { "ammos-${key}":
      source        => $value,
      java_keystore => '/ammos/etc/pki/tls/certs/ammos-truststore.jks',
      notify        => File['/ammos/etc/pki/tls/certs/ammos-truststore.jks'],
    }
  }
  file { '/ammos/etc/pki/tls/certs/ammos-truststore.jks':
    owner   => 'cam-srv',
    group   => 'ammos-tls',
    mode    => '0444',
  }

  file { '/ammos/cam-server/server':
    ensure => 'directory',
    owner  => 'cam-srv',
  }
  exec { 'create-cam-config':
    path        => $facts['path'],
    refreshonly => true,
    cwd         => '/ammos/cam-server/setup/data',
    command     => '/ammos/cam-server/setup/bin/create-cam-config.sh',
    require     => [
      Package['MGSS-ammos-asec-cam-server-5.1.0'],
    ],
    subscribe   => [
      File['/ammos/cam-server/server'],
      File['/ammos/cam-server/setup/data/cam-config-params'],
      File['/ammos/cam-server/setup/data/passwords'],
      File['/ammos/etc/pki/tls/certs/ammos-truststore.jks'],
      File['/ammos/etc/pki/tls/private/ammos-server-keystore.p12'],
    ],
  }
  file_line { 'cam-keystore-type':
    ensure  => present,
    path    => '/ammos/cam-server/setup/SSOAdminTools/cam/bin/ssoadm',
    match   => '^JAVA_OPTS="\$JAVA_OPTS -Djavax.net.ssl.trustStoreType=JKS"',
    line    => 'JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStoreType=JKS"',
    after   => 'JAVA_OPTS="\$JAVA_OPTS -Djavax.net.ssl.trustStore',
    require => Exec['create-cam-config'],
  }
  file_line { 'cam-keystore-password':
    ensure  => present,
    path    => '/ammos/cam-server/setup/SSOAdminTools/cam/bin/ssoadm',
    match   => '^JAVA_OPTS="\$JAVA_OPTS -Djavax.net.ssl.trustStorePassword=changeit"',
    line    => 'JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStorePassword=changeit"',
    after   => 'JAVA_OPTS="\$JAVA_OPTS -Djavax.net.ssl.trustStore',
    require => Exec['create-cam-config'],
  }

  service { 'camserver':
    enable  => true,
    require => Package[$cam_main_package],
  }

  firewalld_port { 'Allow HTTP for CAM':
    ensure   => 'present',
    zone     => 'public',
    port     => 8443,
    protocol => 'tcp',
  }
}