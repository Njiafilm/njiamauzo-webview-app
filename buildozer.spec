[app]
title = NjiaMauzo Afrika
package.name = njiamauzoafrika
package.domain = org.njiamauzo

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3==3.11.6,kivy==2.2.1,pyjnius==1.4.2

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
