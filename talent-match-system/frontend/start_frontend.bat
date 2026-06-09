@echo off

rem 进入前端目录
cd /d %~dp0

rem 安装依赖（使用淘宝源）
echo 正在安装前端依赖...
npm install --registry=https://registry.npmmirror.com

rem 检查依赖安装是否成功
if %errorlevel% neq 0 (
    echo 依赖安装失败，正在重试...
    npm install --registry=https://registry.npmmirror.com
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请检查网络连接或npm配置
        pause
        exit /b 1
    )
)

echo 依赖安装成功，正在启动前端服务...

rem 启动前端服务
npm run dev

pause