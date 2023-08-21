# Handle SELinux modules in CIL format which puppet/selinux module does not.
#
# These are based on the selinux::module puppet module and instructions at
#  https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/creating-selinux-policies-for-containers_using-selinux
# The CIL source can be created after running a container with SELinux in permissive mode with:
#  CTRNAME=anms-core; (cd puppet/modules/anms/files/selinux/ && sudo docker inspect ${CTRNAME} | sudo udica -e docker ${CTRNAME})
#
define anms::semodule_cil(
  String $source_cil,
  Array[String] $extra_cil = [],
) {
  include selinux
  require selinux::build
  require anms::hostenv

  # Variables consistent with selinux::module
  $ensure = 'present'
  $install = true

  $module_dir = $selinux::build::module_build_dir
  $module_file = "${module_dir}/${title}"

  file { "${module_file}.cil":
    ensure  => 'file',
    source  => $source_cil,
    notify  => Exec["clean-module-${title}"],
    require => File[$module_dir],
  }

  exec { "clean-module-${title}":
    path        => '/bin:/usr/bin',
    cwd         => $module_dir,
    command     => "rm -f '${module_file}.loaded'",
    refreshonly => true,
    notify      => Exec["install-module-${title}"],
  }

  if $install {
    $extra_args = join($extra_cil, ' ')

    exec { "install-module-${title}":
      path    => '/sbin:/usr/sbin:/bin:/usr/bin',
      cwd     => $module_dir,
      command => "semodule -i ${module_file}.cil ${extra_args} && touch ${module_file}.loaded",
      creates => "${module_file}.loaded",
      before  => Selmodule[$title],
    }

    # ensure it doesn't get purged if it exists
    file { "${module_file}.loaded": }
  }

  $module_path = ($source_cil != undef) ? {
    true  => "${module_file}.cil",
    false => undef
  }
  selmodule { $title:
    ensure        => $ensure,
    selmodulepath => $module_path,
  }
}
