#!/bin/sh

LOCALPORT=5900
VNCHOST=c7opcp1
VNCPORT=5900
GATEWAY=c7host

ssh -fN -L ${LOCALPORT}:${VNCHOST}:${VNCPORT} ${GATEWAY}

