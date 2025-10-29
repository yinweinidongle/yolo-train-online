@echo off
chcp 65001 >nul
echo ========================================
echo   YOLOv11在线训练平台 - 环境检查
echo ========================================
echo.

set ERRORS=0

echo [1/5] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    echo    请从 https://www.python.org/ 下载并安装Python 3.8+
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python已安装: %%i
)

echo.
echo [2/5] 检查Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装
    echo    请从 https://nodejs.org/ 下载并安装Node.js 16+
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo ✓ Node.js已安装: %%i
)

echo.
echo [3/5] 检查npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm未安装
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo ✓ npm已安装: %%i
)

echo.
echo [4/5] 检查项目结构...
if exist "backend\app.py" (
    echo ✓ 后端文件存在
) else (
    echo ❌ 后端文件缺失
    set /a ERRORS+=1
)

if exist "frontend\package.json" (
    echo ✓ 前端文件存在
) else (
    echo ❌ 前端文件缺失
    set /a ERRORS+=1
)

echo.
echo [5/5] 检查磁盘空间...
for /f "tokens=3" %%i in ('dir /-c ^| find "可用字节"') do (
    echo ✓ 可用磁盘空间充足
)

echo.
echo ========================================
echo   检查完成
echo ========================================
echo.

if %ERRORS% EQU 0 (
    echo ✅ 所有检查通过！
    echo.
    echo 下一步：
    echo   1. 运行 start.bat 启动服务
    echo   2. 或者手动安装依赖：
    echo      - 后端: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    echo      - 前端: cd frontend ^&^& npm install
) else (
    echo ❌ 发现 %ERRORS% 个问题，请先解决上述错误
)

echo.
pause
