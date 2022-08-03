#!/system/bin/sh

MODDIR=${0%/*}
MODULE=$(basename ${MODDIR})

until [ $(getprop sys.boot_completed). = 1. ]; do sleep 1; done
${MODDIR}/system/bin/npem &
