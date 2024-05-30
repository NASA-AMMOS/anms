# Define host environment configuration for ANMS installation.
#
class anms::hostenv(
  Boolean $use_fips = true,
) {
  case $facts['os']['family'] {
    'RedHat':  {
      # This halts on reboot_notify()
      # instead run with:
      #  bolt apply --execute 'class {"fips": }'
      if $use_fips {
        class { 'fips': }
      }

      file { '/var/cache/puppet':
        ensure => 'directory',
        before => Class['selinux'],
      }
      class { 'selinux': }
      package { 'udica':
        ensure  => 'installed',
      }

      class { 'firewalld': }
      firewalld_custom_service { 'ltp':
        ensure => 'present',
        ports  => [
          {
            'port'     => '1113',
            'protocol' => 'udp'
          },
        ],
      }
      firewalld_custom_service { 'dtn-bundle-udp':
        ensure => 'present',
        ports  => [
          {
            'port'     => '4556',
            'protocol' => 'udp'
          },
        ],
      }
      firewalld_service { 'Enable HTTP':
        ensure  => 'present',
        service => 'http',
        zone    => 'public',
      }
      firewalld_service { 'Enable HTTPS':
        ensure  => 'present',
        service => 'https',
        zone    => 'public',
      }
      firewalld_service { 'Enable LTP':
        ensure  => 'present',
        service => 'ltp',
        zone    => 'public',
      }
      firewalld_service { 'Enable UDPCL':
        ensure  => 'present',
        service => 'dtn-bundle-udp',
        zone    => 'public',
      }
    }
    'Debian': {
      case $facts['os']['distro']['codename'] {
        'focal':  {
          if $use_fips {
            # Based on guidance at: https://aplwiki.jhuapl.edu/confluence/pages/viewpage.action?spaceKey=LAPLKEY&title=Ubuntu+FIPS+Packages
            apt::source { 'focal-fips':
              location => 'https://apllinuxdepot.jhuapl.edu/linux/apl-software/focal-fips/',
              release  => '',
              repos    => '/',
              key      => {
                id     => '6F6B15509CF8E59E6E469F327F438280EF8D349F',
                server => 'https://apllinuxdepot.jhuapl.edu/linux/apl-software/focal-fips/apl-software-repo.gpg',
              },
            }

            package { 'ubuntu-fips':
              ensure  => 'installed',
              require => Apt::Source['focal-fips'],
            }
          }
        }
        default: {
          warning("Unhandled OS distro: ${facts['os']['distro']['codename']}")
        }
      }
    }
    default: {
      fail("Unknown OS name ${facts['os']['family']}")
    }
  }

  case $facts['os']['family'] {
    'RedHat':  {
      $ca_cert_path = '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem'
    }
    'Debian': {
      $ca_cert_path = '/etc/ssl/certs/ca-certificates.crt'
    }
    default: {
      fail("Unknown OS family ${facts['os']['family']}")
    }
  }
  augeas { 'environment_ca':
    context => '/files/etc/environment',
    changes => [
      "set PIP_CERT \"${ca_cert_path}\"",
      "set SSL_CERT_FILE \"${ca_cert_path}\"",
    ],
  }

  class { 'anms::docker':
    require => Augeas['environment_ca'],
  }
}
