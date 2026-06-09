@echo off

rem 进入项目根目录
cd /d %~dp0

echo 正在启动人才职位智能匹配与能力图谱系统...

rem 启动后端服务
start "后端服务" cmd /c "cd backend && start_backend.bat"

rem 等待后端服务启动
ping 127.0.0.1 -n 5 > nul

rem 启动前端服务
start "前端服务" cmd /c "cd frontend && start_frontend.bat"

rem 等待前端服务启动
ping 127.0.0.1 -n 10 > nul

rem 打开浏览器访问前端页面
echo 正在打开浏览器...
start http://localhost:5173

echo 系统启动完成，请在浏览器中访问 http://localhost:5173

pause