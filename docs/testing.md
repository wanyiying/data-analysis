> 历史开发记录：其中的测试数、角色执行与正式收尾声明不代表本次验证；以 independent-audit.md 和 release-validation.md 的限制为准。本地 JSON 无法认证真实独立执行。

# 可复现测试

Windows PowerShell，仓库根目录：

实际环境：Python3.11.5 / pandas2.0.3 / numpy1.26.0 / openpyxl3.0.10 / pytest7.4.0。requirements-audit-dev.txt精确记录本次验证环境；上游requirements.txt要求openpyxl>=3.1，本机预装版本低于该声明下限，但实际全部测试通过。未改上游依赖文件，也未声称已验证3.1以上所有版本；面向新环境可在独立虚拟环境按上游依赖安装后重新运行全量测试。

```powershell
python -m pip install -r requirements-audit-dev.txt
$env:PYTHONUTF8='1'
New-Item -ItemType Directory -Path .audit-test-tmp -Force
python -m pytest -q -p no:cacheprovider --basetemp .audit-test-tmp/run-unique-name
python scripts/generate_cross_audit_cases.py
python scripts/run_cross_audit_demos.py
```

每次 basetemp 使用不同名字，避免本机旧目录 ACL。PYTHONUTF8 同时统一父进程 subprocess 的解码和子进程输出；单独 PYTHONIOENCODING=utf-8 会让旧测试父进程仍用 GBK 解码并失败。

实际记录：原默认运行 29 passed/45 errors（ACL）；独立 basetemp 原版 71 passed/3 failed（✓/✗ 的 GBK 输出错误）；只设 PYTHONIOENCODING 原版 50 passed/24 failed（父子编码不同）；设 PYTHONUTF8 后原 74 项加新 48 项，共 122 passed。后续增加安全和独立复算测试，最终结果见 final-delivery.md 与 test-results.xml。

小样本 hand-authored expected 与生产算法分离；随机性质测试固定 seed=7，40 次交换/重排，另检验合法拆分。公开样本单独核对人工注入 -7.25 GBP。未进行真实数据库、生产同步或跨 Python 多版本执行验证。资源是受控上限而非性能承诺。

最终全量：141 passed /0 failed /0 skipped，101.02s；原74项与新增67项。JUnit见test-results.xml。后续针对未知编码受控错误的扩展断言单独运行1 passed；compileall及官方Skill quick_validate通过。汇总见validation-summary.json。
