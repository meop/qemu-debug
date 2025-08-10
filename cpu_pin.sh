#!/bin/zsh

bin='qemu-system-x86_64'
name='glass'
pid=$(pgrep --ignore-ancestors --full --list-full "^${bin}.*${name}" | awk '{print $1}')

# ps -mo pid,tid,fname,user,psr -p
ps -T -p "$pid"
  # pstree -p -a -c -h -s "$pid"
  # ps -efL -p "$pid"


# for tid in $(ps -L -o pid,tid,comm | grep qemu-system | awk '{print $2}'); do
#   # sudo taskset -cp 0,1,2,3 $tid
#   echo $tid
# done
