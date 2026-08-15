# 知识产权·商标专利 每日资讯工作台

全自动、零成本、免密钥：GitHub Actions 每天定时通过 **双通道 RSS** 抓取真实资讯，叠加精选真实历史数据（300+ 条可点原文），重生成单文件 HTML 报告并发布到 GitHub Pages。

八维度：知识产权 / 商标 / 专利 / 项目申报（高企、科小、专精特新等）/ 政策 / 热点案例 / 科普 / 观点。
所有历史条目均来自公开网络真实检索，标题可点击直达原文；历史日为「真实为主、如实留白」——尽力铺满真实资讯，不足的日子不凑数、不编造链接。

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
python3 collect.py --top 20
python3 generate_report.py
```

## 采集引擎（双通道）
- **搜索型 RSS（Google News）**：按各维度关键词搜索，标题直接命中，稳定产出「热点 / 科普 / 观点」等维度。需 GitHub Actions 海外机房网络（国内本地跑可能连不上，会自动静默跳过）。
- **权威媒体 RSS**：人民网 / 新华网 / 中国新闻网 / 钛媒体 / 新浪科技 各频道，国内外均稳定可用，作为兜底。

## 文件说明
- `collect.py` 采集引擎（双通道 RSS，按 URL 去重合并追加）
- `generate_report.py` 报告生成引擎（读 `ip_data.json` → 注入 `template.html`）
- `template.html` 报告模板（单文件、离线可用、内置中英字典）
- `ip_data.json` 资讯数据（合并追加，不覆盖历史）
- `ip_report.html` 最终产物
- `generate_data.py` 精选真实历史数据脚本（生成 2023-03 至 2026-08 的真实资讯，带原文链接）
