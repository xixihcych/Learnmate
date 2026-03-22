# Windows环境配置指南

## PowerShell执行策略问题

如果您在PowerShell中遇到以下错误：
```
无法加载文件 ...\Activate.ps1，因为在此系统上禁止运行脚本
```

## 解决方案（3种方法）

### 方法1: 使用CMD（最简单，推荐）

1. 打开 **命令提示符（CMD）**（不是PowerShell）
2. 运行：

```cmd
cd E:\Learnmate\backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**CMD不受执行策略限制，可以直接使用！**

### 方法2: 修改PowerShell执行策略（一次性设置）

在PowerShell中（以管理员身份运行）：

```powershell
# 查看当前策略
Get-ExecutionPolicy

# 设置为RemoteSigned（推荐）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后就可以正常激活了
venv\Scripts\activate
```

### 方法3: 绕过执行策略（临时）

在PowerShell中：

```powershell
# 方法3a: 使用批处理文件
.\activate_env.bat

# 方法3b: 直接调用（绕过策略）
& venv\Scripts\Activate.ps1

# 方法3c: 使用CMD启动
cmd /c "venv\Scripts\activate && python -m uvicorn main:app --reload"
```

### 方法4: 不激活环境，直接使用（最简单）

**不需要激活环境！** 直接使用虚拟环境中的Python：

```powershell
# 安装依赖
venv\Scripts\python.exe -m pip install -r requirements.txt

# 运行服务
venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 推荐方案

**最简单的方法**：使用CMD而不是PowerShell

1. 按 `Win + R`
2. 输入 `cmd` 回车
3. 运行：

```cmd
cd E:\Learnmate\backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 快速启动脚本

已创建 `activate_env.bat`，双击即可激活环境并打开CMD窗口。

## 验证环境

激活后验证：

```cmd
python --version
pip --version
pip list
```






