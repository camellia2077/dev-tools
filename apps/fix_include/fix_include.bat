@echo off
cd /d %~dp0\..\..
python -m dev_tools fix-include %*
