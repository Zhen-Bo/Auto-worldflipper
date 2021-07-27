@ECHO OFF
chcp 65001
IF NOT EXIST adb.exe GOTO notexist
:loop
cls
@ECHO 請輸入模擬器IP跟port (Ex:127.0.0.1:5555)
@SET /p port=請輸入: 
adb.exe connect %port%
PAUSE
goto loop
:notexist
@ECHO 路徑錯誤
PAUSE