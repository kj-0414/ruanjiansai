@echo off

rem 进入后端目录
cd /d %~dp0

rem 安装依赖
echo 正在安装后端依赖...
pip install -r requirements.txt

rem 检查依赖安装是否成功
if %errorlevel% neq 0 (
    echo 依赖安装失败，正在重试...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请检查网络连接或pip配置
        pause
        exit /b 1
    )
)

echo 依赖安装成功，正在启动后端服务...

rem 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause