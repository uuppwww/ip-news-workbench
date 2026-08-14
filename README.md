# 知识产权·商标专利 每日资讯工作台

全自动、零成本、免密钥：GitHub Actions 每天定时通过 RSS 抓取四维度资讯
（国家政策 / 动态 / 热点 / 行业基本面），重生成单文件 HTML 报告并发布到 GitHub Pages。

## 你每天要做的
- 什么也不用做。打开下面的链接就是当天最新报告：
  `https://<你的用户名>.github.io/<仓库名>/ip_report.html`

## 想马上更新一次
- 进仓库 **Actions → 每日知识产权资讯更新 → Run workflow**，点一下即可立即重跑。

## 改自动时间
- 编辑 `.github/workflows/daily.yml` 里的 `cron: '7 8 * * *'`（UTC 时间）。

## 本地手动跑（可选）
```bash
pip install -r requirements.txt
SEARCH_ENGINE=rss ./refresh.sh --top 10   # 需要 refresh.sh；或：
python3 collect.py --top 10 && python3 generate_report.py
```

## 文件说明
- `collect.py` 采集引擎（RSS 免密钥，另支持 bing/serpapi/gcse）
- `generate_report.py` 重生成引擎（读 ip_data.json → 注入 template.html）
- `template.html` 报告模板（内置中英字典、支持 ?lang=en）
- `ip_data.json` 资讯数据（每日被 RSS 结果覆盖；抓到 0 条时保留上一份）
- `ip_report.html` 最终产物（单文件、可离线、双语）
