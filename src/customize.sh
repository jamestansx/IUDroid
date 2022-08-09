#!/sbin/sh

# microG GmsCore needs to be installed as user app for all permissions to be granted
# see https://github.com/microg/android_packages_apps_GmsCore/issues/1100#issuecomment-711088518
pm install --dont-kill -g "${MODPATH}/system/priv-app/GmsCore/GmsCore.apk"

# Fix Trime keep crashing as System App
trime="${MODPATH}/system/app/Trime/Trime.apk"
[ -f $trime ] && pm install --dont-kill -g $trime
