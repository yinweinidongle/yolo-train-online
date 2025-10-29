@echo off
chcp 65001 >nul
echo ========================================
echo   YOLOv11在线训练平台 - 启动脚本
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo [1/4] 检查后端虚拟环境...
if not exist "backend\venv" (
    echo [信息] 创建Python虚拟环境...
    cd backend
    python -m venv venv
    cd ..
)

echo [2/4] 检查后端依赖...
if not exist "backend\venv\Lib\site-packages\flask" (
    echo [信息] 安装后端依赖（首次运行可能需要几分钟）...
    cd backend
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)

echo [3/4] 检查前端依赖...
if not exist "frontend\node_modules" (
    echo [信息] 安装前端依赖（首次运行可能需要几分钟）...
    cd frontend
    call npm install
    cd ..
)

echo [4/4] 启动服务...
echo.
echo ========================================
echo   启动后端服务 (http://localhost:5000)
echo ========================================
start "YOLOv11后端" cmd /k "cd backend && call venv\Scripts\activate && python app.py"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   启动前端服务 (http://localhost:3000)
echo ========================================
start "YOLOv11前端" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   服务已启动！
echo ========================================
echo.
echo 后端地址: http://localhost:5000
echo 前端地址: http://localhost:3000
echo.
echo 请等待几秒钟，然后在浏览器中打开前端地址
echo.
echo 提示：关闭此窗口不会停止服务
echo       要停止服务，请关闭弹出的两个命令行窗口
echo.

timeout /t 3 /nobreak >nul
start http://localhost:3000

pause
