#!/bin/sh
{# This script template uses both shell-script and Jinja formatting. #}
{# Consider breaking out the loop into separate units run independently? #}
ip addr show dev {{ ansible_default_ipv4.interface }} | sed s/^/./
route -n
ping -n -c 2 -W 1 {{ ansible_default_ipv4.gateway }}
{% if 'gateway' in ansible_default_ipv6 %}
route -n -6
ping -6 -n -c 2 -W 1 -I {{ ansible_default_ipv6.interface }} {{ ansible_default_ipv6.gateway }}
{% endif %}
netstat -nt
for h in {{ host_list | difference([inventory_hostname]) | sort | list | join(' ') }}; do
  host -t any $h
  ping -4 -n -c 2 -W 1 $h || traceroute -4 -n $h
{% if 'gateway' in ansible_default_ipv6 %}
  if x=$(host -t aaaa $h); then
    case "$x" in
      *"has no AAAA record"*) ;;
      *) ping -6 -n -c 2 -W 1 $h || traceroute -6 -n $h ;;
    esac
  fi
{% endif %}
done
