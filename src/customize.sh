#!/sbin/sh

SWIPE_LIBDIR="lib"
SWIPE_DEST="/system/${SWIPE_LIBDIR}"
ARCH="arm64"

reset_runtime_permissions () {
    # required on Android 10, else all apps bundled with NanoDroid will not
    # show a permission prompt for android.permission.WRITE_EXTERNAL_STORAGE
    if [ "${API}" -ge 29 ]; then
	pm reset-permissions
    fi
}

link_swipe_libs () {
    DEST_IME=${1}
    if [ -f "${DEST_IME}/libjni_latinime.so" ]; then
	mkdir -p "${MODPATH}${DEST_IME}"
	ln -sfn "${MODPATH}${SWIPE_DEST}/libjni_latinimegoogle.so" "${MODPATH}${DEST_IME}/libjni_latinime.so"
	ln -sfn "${MODPATH}${SWIPE_DEST}/libjni_keyboarddecoder.so" "${MODPATH}${DEST_IME}/libjni_keyboarddecoder.so"

    elif [ -f "${DEST_IME}/libjni_latinimegoogle.so" ]; then
	mkdir -p "${MODPATH}${DEST_IME}"
	ln -sfn "${MODPATH}${SWIPE_DEST}/libjni_latinimegoogle.so" "${MODPATH}${DEST_IME}/libjni_latinimegoogle.so"
	ln -sfn "${MODPATH}${SWIPE_DEST}/libjni_keyboarddecoder.so" "${MODPATH}${DEST_IME}/libjni_keyboarddecoder.so"
    fi
}

###########################################################################################
# Main Script
###########################################################################################

#link_swipe_libs "/system/product/app/LatinIME/${SWIPE_LIBDIR}/${ARCH}"

# microG GmsCore needs to be installed as user app for all permissions to be granted
# see https://github.com/microg/android_packages_apps_GmsCore/issues/1100#issuecomment-711088518
pm install --dont-kill -g "${MODPATH}/system/priv-app/GmsCore/GmsCore.apk"

#reset_runtime_permissions
