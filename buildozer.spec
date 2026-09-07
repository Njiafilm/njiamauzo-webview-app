[app]
title = NjiaMauzo Afrika
icon.filename = %(source.dir)s/logo.png
package.name = njiamauzoafrika
package.domain = org.njiamauzo

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3==3.11.6,hostpython3==3.11.6,kivy,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
