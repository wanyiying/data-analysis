# 本地复现

在仓库根目录执行，推荐 Python 3.11。运行自带合成/公开派生样本无需下载原始大文件，也无需 API 密钥。不要把真实企业数据复制进仓库。

## Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-audit-dev.txt
New-Item -ItemType Directory -Path .audit-test-tmp -Force | Out-Null
$env:PYTHONUTF8='1'
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp .audit-test-tmp/fresh-run --junitxml outputs/local-tests.xml
.\.venv\Scripts\python.exe scripts/run_cross_audit_demos.py
```

每次使用新的 basetemp 目录名。outputs/cross-audit-demos/index.json 列出四次运行目录，打开各目录 report.html。退出码 consistent=0、value_mismatch=1、definition=3、public_retail=1；差异与不可比是预期演示结果。所有自动 Demo 保持 degraded；不调用正式收尾。

requirements-audit-dev.txt 锁定历史实测环境，含 openpyxl 3.0.10，低于上游 requirements.txt 的 >=3.1 声明；该文件用于复现实测，不是生产依赖推荐。若按上游 requirements.txt 安装新版本，需自行重跑测试，不能沿用旧通过声明。本次没有验证新的安装环境或多版本矩阵。

样例输出属于本地生成文件，manifest 中绝对路径须在本机重新生成。导出明细核验只证明所导出工件的内部一致性，不是从原始输入重新实现的第二套对账系统。
