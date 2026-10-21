@echo off
rem Kurulum yapmadan Windows'ta çalıştırma: gpower-clone.cmd --test chi2-contingency ...
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"
python -m powerchi %*
