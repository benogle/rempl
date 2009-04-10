rem This is mostly intended to be used as a helper app in firefox for pls and m3u playlist files.
rem Yes, the path must be absolute as the cwd when called is firefox's app dir. So you have to change it. :(

set AJAXAMP_ADDR=http://192.168.1.100:5151
set REMPL_PATH=D:\work\git\rempl\rempl.py

python %REMPL_PATH% -s %AJAXAMP_ADDR% %1
