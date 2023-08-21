# As a precondition:
# sudo update-alternatives --install /usr/bin/puppet puppet-agent /opt/puppetlabs/bin/puppet 10
# sudo curl -sL http://apllinuxdepot.jhuapl.edu/linux/APL-root-cert/JHUAPL-MS-Root-CA-05-21-2038-B64-text.cer -o /etc/pki/ca-trust/source/anchors/JHUAPL-MS-Root-CA-05-21-2038-B64-text.crt && sudo update-ca-trust
#
# Apply with:
# sudo puppet apply --hiera_config hiera.yaml --modulepath modules:.modules manifests/test-camserver.pp --test

node default {
  yumrepo { 'anms-deployment':
    baseurl  => 'https://artifactory.jhuapl.edu/artifactory/rpm-local/anms/deployment/',
    enabled  => 1,
    gpgcheck => 0,
  }
  -> class { 'apl_test::camserver':
  }
}
