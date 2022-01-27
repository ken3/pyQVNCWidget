#!/bin/bash

source /etc/profile

export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
export DISPLAY=:1.0

SYSFONTDIR=/usr/share/X11/fonts
FONTPATH="$SYSFONTDIR/misc,$SYSFONTDIR/Type1"
SCREENS="-screen 0 1200x800x24"
VFB_OPTS="$SCREENS -nolock -ac -br -audit 0"
VFB_OPTS="$VFB_OPTS -fp $FONTPATH"
VFB_OPTS="$VFB_OPTS r -ardelay 500 -arinterval 50"
VNC_OPTS="-repeat -speeds lan -v -forever -shared -sb 0"
VNC_OPTS="$VNC_OPTS"

(
  killall -w Xvfb x11vnc
  sleep 1

  nohup Xvfb :1 $VFB_OPTS &

  for i in 1 2 3 4 5 6 7 8 9 10
  do
    xset q && break
    sleep 1
  done

  nohup x11vnc -rfbport 5900 $VNC_OPTS &

  nohup mwm &
) >/dev/null 2>&1

echo "`basename $0`: done."

