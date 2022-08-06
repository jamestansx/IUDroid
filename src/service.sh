#!/system/bin/sh

MODDIR=${0%/*}
MODULE=$(basename ${MODDIR})

run_initscripts () {
    until [ $(getprop sys.boot_completed). = 1. ]; do sleep 1; done
    for init in 10_sqlite 20_fstrim 30_logcat 40_logscleaner; do
	    if [ -f "${MODDIR}/common/${init}" ]; then
		    "${MODDIR}/common/${init}" &
	    fi
    done
}

until [ $(getprop sys.boot_completed). = 1. ]; do sleep 1; done
${MODDIR}/system/bin/npem &
run_initscripts &
