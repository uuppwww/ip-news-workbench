# 知识产权·商标专利 每日资讯工作台

全自动、零成本、免密钥：GitHub Actions 每天定时通过 RSS 抓取四维度资讯
（国家政策 / 行业动态 / 热点案例 / 国际基本面），重生成单文件 HTML 报告并发布到 GitHub Pages。

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
- `generate_data.py` 离线填充脚本（当 RSS 采集失败时，可生成每日基础数据）
