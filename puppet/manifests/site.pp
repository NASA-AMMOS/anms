# As a precondition:
# sudo update-alternatives --install /usr/bin/puppet puppet-agent /opt/puppetlabs/bin/puppet 10

node default {
  class { 'anms': }
}
