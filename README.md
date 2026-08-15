# 知识产权·商标专利 每日资讯工作台

全自动、零成本、免密钥：GitHub Actions 每天定时通过 RSS 抓取真实资讯，叠加精选真实历史数据（45+ 条可点原文），重生成单文件 HTML 报告并发布到 GitHub Pages。

六维度：知识产权 / 商标 / 专利 / 项目申报（高企、科小、专精特新等）/ 政策 / 热点案例。
所有历史条目均来自公开网络真实检索，标题可点击直达原文。

## 访问地址
- 首页：`https://<你的用户名>.github.io/<仓库名>/`
- 报告页：`https://<你的用户名>.github.io/<仓库名>/ip_report.html`
- 英文版：在报告页地址后加 `?lang=en`

## 你每天要做的事
- 什么也不用做。打开上面的链接就是当天最新报告。

## 想马上更新一次
- 进仓库 **Actions → Daily IP News Update → Run workflow**，点一下即可立即重跑。

## 修改自动更新时间
- 编辑 `.github/workflows/daily.yml` 里的 `cron: '7 8 * * *'`（UTC 时间，对应北京时间 16:07）。

## 本地手动跑（可选）
```bash
pip install -r requirements.txt
python3 collect.py --top 10
python3 generate_report.py
```

## 文件说明
- `collect.py` 采集引擎（RSS 免密钥，按 URL 去重合并追加）
- `generate_report.py` 报告生成引擎（读 `ip_data.json` → 注入 `template.html`）
- `template.html` 报告模板（单文件、离线可用、内置中英字典）
- `ip_data.json` 资讯数据（合并追加，不覆盖历史）
- `ip_report.html` 最终产物
- `generate_data.py` 精选真实历史数据脚本（生成 2023-09 至 2026-06 的 45 条真实资讯，带原文链接）
