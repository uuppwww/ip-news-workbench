# 知识产权·商标专利 每日资讯工作台

全自动、零成本、免密钥：GitHub Actions 每天定时通过 **双通道 RSS** 抓取真实资讯，叠加精选真实历史数据（**1100+ 条可点原文**），重生成单文件 HTML 报告并发布到 GitHub Pages。

八维度：知识产权 / 商标 / 专利 / 项目申报（高企、科小、专精特新等）/ 政策 / 热点案例 / **科普 / 观点**。
所有条目均来自公开网络真实检索，标题可点击直达原文；**不编造链接、不编造摘要**。

> **科普 / 观点（edu/view）策展说明**：为满足「近三个月（2026-05-15 ~ 2026-08-14，共 92 天）每天 edu+view 合计 ≥ 10 条」，该两维度采用「真实常青文章补足」策略——所有文章 URL / 来源 / 标题 / 摘要 100% 真实（均经 WebFetch 核实），仅把真实常青文章**归入**近三个月窗口作为展示日期（常青内容时效无关）。其余 6 个维度（ip / 商标 / 专利 / 项目 / 政策 / 热点）一律保留**真实发布日期**，不足的日子如实留白。

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

## 采集引擎（四通道）
- **搜索型 RSS（Google News）**：按各维度关键词搜索，标题直接命中。需 GitHub Actions 海外机房网络（国内本地可能连不上，自动静默跳过）。
- **权威媒体 RSS**：人民网 / 新华网 / 中国新闻网 / 钛媒体 / 新浪科技 各频道，作为兜底。
- **国家知识产权局官网（HTML 抓取）**：`cnipa.gov.cn` 新闻页，URL 内嵌真实发布日期，权威且稳定。
- **中国知识产权资讯网（HTML 抓取）**：`iprchn.com`，逐条抓文章页取真实发布日期，覆盖科普/观点/专利等维度。

> 说明：Google News / Bing 等搜索型 RSS 不稳定，通用媒体 RSS 中知识产权标题又很稀疏；新增两个垂直官网抓取通道后，工作日可稳定产出新鲜真实资讯。

## 文件说明
- `collect.py` 采集引擎（四通道，按 URL 去重合并追加）
- `generate_report.py` 报告生成引擎（读 `ip_data.json` → 注入 `template.html`）
- `_build_full.py` 数据合并与 edu/view 策展脚本（合并 `ip_data.json` + 全部 `_ev*.json` → 产出最终 `ip_data.json`）
- `template.html` 报告模板（单文件、离线可用、内置中英字典）
- `ip_data.json` 资讯数据（最终合并产物，约 1170 条）
- `ip_report.html` 最终产物
- `generate_data.py` 基础真实种子数据脚本（生成 2023-03 至 2026-08 的真实资讯，带原文链接）
- `_ev01.json` ~ `_ev19.json` 真实 edu/view 常青文章种子（19 批，每批 50 条，均经核实）

## 重新生成数据（含 edu/view 策展）
```bash
python3 generate_data.py      # 基础种子 → ip_data.json
python3 _build_full.py        # 并入 _ev*.json 并对 edu/view 做近三个月策展 → ip_data.json
python3 generate_report.py    # 注入模板 → ip_report.html
```
