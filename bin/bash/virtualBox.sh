#!/usr/bin/env bash

#############################################################################
virtualBoxAttachDisks() {
  local virtualBox=$1
  shift
  let sataPort=$1
  shift

  if [ ${#*} -gt 0 ]; then
    virtualBoxStop ${virtualBox}
    for diskPath in "${@}"; do
      >&/dev/null vboxmanage storageattach ${virtualBox} \
        --storagectl "SATA Controller" --port ${sataPort} --device 0  \
        --type hdd --medium "${diskPath}"
      let sataPort++
    done
    virtualBoxStart ${virtualBox}
  fi
}

#############################################################################
virtualBoxCreateDisk() {
  local virtualBox=$1
  local diskName=${virtualBox}-$2
  let size=$3*1024 # sizes are specified in G, but virtualbox wants M

  local configFolder=$(virtualBoxGetConfigFolder ${virtualBox})
  local diskPath="${configFolder}"/${diskName}

  local output=""
  if [ ! -e "${diskPath}".vdi ]; then
    >&/dev/null vboxmanage createmedium disk --filename "$diskPath"  \
      --size ${size} --format VDI
    output="${diskPath}".vdi
  fi

  echo "${output}"
}

#############################################################################
virtualBoxGetAttribute () {
  local virtualBox=$1
  local attribute=$2

  echo $(vboxmanage showvminfo ${virtualBox} --machinereadable  \
          | grep "${attribute}="  \
          | sed -E -e "s/${attribute}=\"(.*)\"/\1/")
}

#############################################################################
virtualBoxGetConfigFolder () {
  local virtualBox=$1

  echo $(virtualBoxGetAttribute ${virtualBox} CfgFile \
          | sed -E -e "s/(.*)\/.+\.vbox/\1/")
}

#############################################################################
virtualBoxProvision() {
  local virtualBox=$1
  shift

  declare -a disks
  let index=0
  for size in ${@}; do
    local disk=$(virtualBoxCreateDisk ${virtualBox} disk${index} ${size})
    if [ ! -z "${disk}" ]; then
      disks[${index}]="${disk}"
      let index++
    fi
  done

  virtualBoxAttachDisks ${virtualBox} 2 "${disks[@]}"
}

#############################################################################
virtualBoxStart() {
  local virtualBox=$1

  >&/dev/null vboxmanage startvm ${virtualBox} --type headless
  while [ "$(virtualBoxGetAttribute ${virtualBox} VMState)" != "running" ]; do
    sleep 10
  done
}

#############################################################################
virtualBoxStop() {
  local virtualBox=$1

  >&/dev/null vboxmanage controlvm ${virtualBox} acpipowerbutton
  while [ "$(virtualBoxGetAttribute ${virtualBox} VMState)" != "poweroff" ]; do
    sleep 10
  done
}

#############################################################################
#############################################################################
FUNCTION=$1
shift
${FUNCTION} "${@}"
