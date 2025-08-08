#!/bin/bash

for pid in $(pgrep --ignore-ancestors --full --list-full "^qemu-system-x86_64.*glass" | awk '{print $1}'); do
  ps -T -p "$pid"
  pstree -p -a -c -h -s "$pid"
  ps -efL -p "$pid"
done

# for tid in $(ps -L -o pid,tid,comm | grep qemu-system | awk '{print $2}'); do
#   # sudo taskset -cp 0,1,2,3 $tid
#   echo $tid
# done
