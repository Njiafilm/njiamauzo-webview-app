[app]
title = NJIAFIX MOBILE
package.name = njiafixmobile
package.domain = org.njiafix

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

# Permissions this app actually uses:
# INTERNET / ACCESS_NETWORK_STATE - for the real reachability check
# WRITE_EXTERNAL_STORAGE (legacy, <=Android 9) - for "Hifadhi Ripoti"
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
