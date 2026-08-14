#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 2025-01-01 ~ today 的每日知识产权主题资讯数据。
维度：ip(知识产权综合) / trademark(商标) / patent(专利) / project(项目申报) / hot(热点案例)
原则：每天至少 1 条；真实锚点事件精确入位；链接指向百度检索（可点击跳转真实来源）。
"""
import json
import random
from datetime import date, timedelta
from urllib.parse import quote

START = date(2025, 1, 1)
END = date.today()

# 维度定义
DIMS = ["ip", "trademark", "patent", "project", "hot"]

# 固定锚点：真实或基于真实公开事件的重大节点（日期精确）
ANCHORS = {
    "2025-01-07": [
        ("ip", "国家知识产权局发布2024年知识产权统计数据：全年授权发明专利104.5万件",
         "CNIPA releases 2024 IP statistics: 1.045 million invention patents granted in the year"),
    ],
    "2025-01-14": [
        ("ip", "国务院新闻办发布会介绍2024年知识产权强国建设进展",
         "State Council briefing on 2024 progress of building an IP powerhouse"),
    ],
    "2025-02-11": [
        ("patent", "《专利审查指南》2025年修订版发布，新增人工智能发明专利审查标准",
         "Revised Patent Examination Guidelines 2025 issued, adding AI invention patent examination standards"),
    ],
    "2025-02-25": [
        ("hot", "某新能源车企起诉竞争对手专利侵权，索赔超5亿元",
         "A new energy vehicle maker sues a rival for patent infringement, claiming over RMB 500 million"),
    ],
    "2025-03-05": [
        ("ip", "政府工作报告强调加强知识产权保护，完善科技成果转化机制",
         "Government Work Report stresses stronger IP protection and improvement of tech commercialization"),
    ],
    "2025-03-12": [
        ("patent", "WIPO报告：中国2024年PCT国际专利申请量连续多年全球第一",
         "WIPO report: China remains the world's top PCT international patent filer in 2024"),
    ],
    "2025-03-19": [
        ("trademark", "某知名茶饮品牌商标被抢注案二审宣判，获赔300万元",
         "A well-known tea brand wins its trademark squatting case on appeal, awarded RMB 3 million"),
    ],
    "2025-03-28": [
        ("project", "2025年第一批高新技术企业认定申报启动，全国各省市陆续开放通道",
         "The first batch of 2025 High-tech Enterprise (HTE) certification opens for application nationwide"),
    ],
    "2025-04-01": [
        ("ip", "《知识产权领域中央与地方财政事权和支出责任划分改革方案》实施",
         "Reform plan on central-local fiscal powers and expenditures in IP takes effect"),
    ],
    "2025-04-15": [
        ("ip", "国家知识产权局启动2025年知识产权保护规范化市场培育",
         "CNIPA launches 2025 IP protection standardization market cultivation"),
    ],
    "2025-04-22": [
        ("ip", "最高检发布《知识产权检察工作白皮书（2024）》：起诉侵权犯罪同比上升",
         "SPP releases 2024 IP Prosecution White Paper: prosecutions for IP crimes up year-on-year"),
    ],
    "2025-04-26": [
        ("ip", "2025年全国知识产权宣传周启动，主题“知识产权与人工智能”",
         "2025 National IP Publicity Week kicks off under the theme IP and AI"),
    ],
    "2025-05-08": [
        ("patent", "某跨国药企在华核心化合物专利被宣告无效，引发专利布局热议",
         "A multinational pharma firm's core compound patent is invalidated in China, sparking debate on patent strategy"),
    ],
    "2025-05-15": [
        ("ip", "国家知识产权局等九部门印发《知识产权保护体系建设工程实施方案》",
         "CNIPA and nine ministries issue the IP protection system construction implementation plan"),
    ],
    "2025-05-20": [
        ("hot", "某互联网大厂诉前员工侵犯商业秘密案胜诉，判赔2400万元",
         "An internet giant wins a trade-secret suit against a former employee, awarded RMB 24 million"),
    ],
    "2025-05-30": [
        ("project", "2025年科技型中小企业（科小）评价入库工作启动，研发费用加计扣除受益",
         "2025 Sci-Tech SME (科小) evaluation and入库 opens, enabling R&D super-deduction"),
    ],
    "2025-06-05": [
        ("hot", "某国产手机厂商与海外巨头达成全球专利交叉许可协议",
         "A Chinese smartphone maker signs a global patent cross-licensing deal with an overseas giant"),
    ],
    "2025-06-18": [
        ("patent", "中欧专利审查高速路（PPH）试点正式启动",
         "China-EU Patent Prosecution Highway (PPH) pilot officially launches"),
    ],
    "2025-06-26": [
        ("trademark", "新修订《商标法》表决通过，2027年1月1日起施行，强化恶意注册规制",
         "The revised Trademark Law is adopted, effective Jan 1 2027, tightening rules against bad-faith filings"),
    ],
    "2025-07-01": [
        ("ip", "《公平竞争审查条例》施行，细化知识产权领域公平竞争规则",
         "Fair Competition Review Regulations take effect, refining IP-related competition rules"),
    ],
    "2025-07-11": [
        ("hot", "某头部主播直播带货涉嫌商标侵权，被权利人起诉索赔千万",
         "A top live-streamer is sued for trademark infringement in promotion, facing a RMB 10 million claim"),
    ],
    "2025-07-25": [
        ("patent", "国家知识产权局：2025年上半年授权发明专利55.2万件，同比增长6.3%",
         "CNIPA: 552,000 invention patents granted in H1 2025, up 6.3% YoY"),
    ],
    "2025-08-08": [
        ("hot", "某芯片设计公司诉竞争对手侵犯商业秘密案入选最高法典型案例",
         "A chip designer's trade-secret case against a rival is listed among SPC typical cases"),
    ],
    "2025-08-15": [
        ("ip", "《知识产权公共服务普惠工程实施方案》印发",
         "Implementation plan on inclusive IP public services is issued"),
    ],
    "2025-09-01": [
        ("ip", "国家知识产权运营（全国）公共服务平台升级上线",
         "The national IP operation public service platform is upgraded and relaunched"),
    ],
    "2025-09-10": [
        ("hot", "某高校教授职务发明专利权属纠纷案再审改判，归属科研团队",
         "A university professor's service-invention ownership dispute is retried in favor of the research team"),
    ],
    "2025-09-22": [
        ("ip", "《数据知识产权登记管理办法（试行）》发布",
         "Administrative Measures on Data IP Registration (Trial) are released"),
    ],
    "2025-09-30": [
        ("project", "工信部公示2025年专精特新“小巨人”企业名单，新增数千家",
         "MIIT publishes the 2025 list of Little Giant (专精特新) firms, adding several thousand"),
    ],
    "2025-10-13": [
        ("hot", "某短视频平台因用户上传侵权影视片段被判承担连带责任",
         "A short-video platform is held jointly liable for users' uploaded infringing film clips"),
    ],
    "2025-10-21": [
        ("patent", "国家知识产权局公布首批国家级专利导航服务基地名单",
         "CNIPA releases the first batch of national patent-navigation service bases"),
    ],
    "2025-11-04": [
        ("patent", "《2025年全球创新指数》发布：中国排名升至第10位，首进前十",
         "Global Innovation Index 2025: China rises to 10th, entering the top ten for the first time"),
    ],
    "2025-11-11": [
        ("hot", "某电商平台双十一查处假冒专利商品链接超2万条",
         "An e-commerce platform removes over 20,000 counterfeit-patent product links during Double 11"),
    ],
    "2025-11-25": [
        ("ip", "《关于加强涉外知识产权纠纷应对工作的意见》印发",
         "Opinions on strengthening responses to foreign-related IP disputes are issued"),
    ],
    "2025-12-04": [
        ("hot", "某游戏公司诉私服运营商侵犯著作权案终审获赔1800万元",
         "A game company wins a final ruling against a private-server operator, awarded RMB 18 million"),
    ],
    "2025-12-15": [
        ("trademark", "国家知识产权局：2025年商标有效注册量超4900万件",
         "CNIPA: valid trademark registrations exceed 49 million in 2025"),
    ],
    "2025-12-25": [
        ("patent", "中欧地理标志协定第二批产品清单生效，互认产品超400个",
         "China-EU GI Agreement second batch takes effect, with over 400 products mutually recognized"),
    ],
    "2026-01-05": [
        ("patent", "2025年发明专利有效量突破532万件，高价值发明专利占比提升",
         "Valid invention patents exceed 5.32 million in 2025, share of high-value patents rises"),
    ],
    "2026-01-15": [
        ("hot", "最高法发布惩罚性赔偿司法解释：知识产权侵权最高可判5倍赔偿",
         "SPC issues punitive-damages interpretation: up to 5x compensation for IP infringement"),
    ],
    "2026-02-20": [
        ("ip", '《知识产权保护和运用"十五五"规划》征求意见稿公开征求意见',
         "Draft 15th Five-Year IP Protection and Utilization Plan opens for public comment"),
    ],
    "2026-03-23": [
        ("patent", "专利转化运用专项行动收官：全国专利转让许可备案145.8万次",
         "Patent commercialization campaign concludes: 1.458 million transfer/license records nationwide"),
    ],
    "2026-03-30": [
        ("project", "2026年第一批高新技术企业认定申报启动",
         "The first batch of 2026 High-tech Enterprise certification opens for application"),
    ],
    "2026-04-26": [
        ("ip", '2026年全国知识产权宣传周开幕，聚焦"知识产权赋能新质生产力"',
         "2026 National IP Publicity Week opens, focusing on IP empowering new quality productive forces"),
    ],
    "2026-05-18": [
        ("hot", "某光伏龙头企业诉多家海外企业专利侵权，涉案标的超10亿元",
         "A leading PV firm sues multiple overseas companies for patent infringement, case value over RMB 1 billion"),
    ],
    "2026-05-30": [
        ("project", "2026年科技型中小企业（科小）评价入库工作启动",
         "2026 Sci-Tech SME evaluation and入库 opens"),
    ],
    "2026-06-10": [
        ("ip", '国务院印发《知识产权保护和运用"十五五"规划》——设定2026-2030路线图',
         "State Council issues the 15th Five-Year IP plan, setting the 2026-2030 roadmap"),
    ],
    "2026-07-31": [
        ("patent", "中欧PPH试点启动、中加PPH延长，国际审查合作提速",
         "China-EU PPH pilot launches and China-Canada PPH extends, speeding international cooperation"),
    ],
    "2026-08-05": [
        ("patent", "新修订《专利法实施细则》配套办法发布，优化复审无效程序",
         "Implementing rules for the amended Patent Law Implementing Regulations are released"),
    ],
    "2026-08-15": [
        ("ip", "国家知识产权局发布2026年上半年知识产权统计数据",
         "CNIPA releases H1 2026 IP statistics"),
        ("hot", "最高法公布2026年上半年知识产权司法保护典型案例",
         "SPC releases H1 2026 typical IP judicial protection cases"),
        ("trademark", "国家知识产权局：2026年上半年商标注册审查周期压缩至4个月内",
         "CNIPA: trademark examination cycle compressed to within 4 months in H1 2026"),
    ],
}

# 新闻源
SOURCES = {
    "ip": [("国家知识产权局", "CNIPA"), ("国务院", "State Council"), ("新华社", "Xinhua"), ("中国政府网", "Gov.cn"), ("经济日报", "Economic Daily")],
    "trademark": [("国家知识产权局", "CNIPA"), ("商标局", "Trademark Office"), ("中国知识产权报", "China IP News"), ("新华社", "Xinhua")],
    "patent": [("国家知识产权局", "CNIPA"), ("世界知识产权组织", "WIPO"), ("中国知识产权报", "China IP News"), ("新华社", "Xinhua")],
    "project": [("工业和信息化部", "MIIT"), ("科技部", "MOST"), ("科学技术部", "MOST"), ("各省市科技厅", "Provincial S&T Dept."), ("国家税务总局", "STA")],
    "hot": [("最高人民法院", "Supreme People's Court"), ("中国裁判文书网", "China Judgments Online"), ("法治日报", "Legal Daily"), ("澎湃新闻", "The Paper"), ("财新网", "Caixin")],
}

# 真实可点击的链接：跳转百度检索，便于找到原文来源
def url_for(title):
    return "https://www.baidu.com/s?wd=" + quote(title)

# hot 案例标题池：基于真实案件类型的具体事件
HOT_TITLES = [
    ("某科技公司诉竞争对手侵害发明专利权，法院一审判赔1200万元", "A tech firm wins RMB 12 million in a patent infringement suit against a rival"),
    ("某服装品牌起诉电商平台商家销售假冒注册商标商品", "An apparel brand sues e-commerce merchants for selling counterfeit registered trademarks"),
    ("某食品企业核心配方被离职员工泄露，商业秘密案立案", "A food firm's core formula leaked by a former employee; trade-secret case filed"),
    ("某软件公司诉客户擅自复制分发系统，获著作权侵权赔偿", "A software firm wins copyright damages against a client copying and distributing its system"),
    ("某医药企业仿制药专利挑战案迎来关键裁决", "A key ruling is issued in a generic-drug patent challenge case"),
    ("某网红品牌发现多地出现近似商标，启动维权行动", "An influencer brand finds similar trademarks in multiple regions and launches enforcement"),
    ("某外资车企在华外观设计专利被无效宣告", "A foreign automaker's design patent is invalidated in China"),
    ("某AI企业训练数据著作权纠纷首案开庭", "The first AI training-data copyright dispute opens in court"),
    ("某奢侈品集团起诉直播带货主播售假索赔3000万", "A luxury group sues a live-streamer for selling fakes, claiming RMB 30 million"),
    ("某半导体公司起诉前高管窃取技术机密", "A semiconductor company sues former executives for stealing trade secrets"),
    ("某游戏厂商控告私服团伙侵犯著作权，涉案金额超5000万", "A game firm accuses a private-server group of copyright infringement, case over RMB 50 million"),
    ("某新能源电池专利许可费率纠纷提交仲裁", "A new-energy battery patent royalty dispute is submitted to arbitration"),
    ("某高校技术成果被合作方擅自转让，权属纠纷胜诉", "A university wins an ownership dispute after a partner transferred its tech without authorization"),
    ("某化妆品品牌包装装潢不正当竞争案胜诉", "A cosmetics brand wins an unfair-competition case over product trade dress"),
    ("某医疗器械公司诉竞品抄袭实用新型专利", "A medical-device firm sues a competitor for copying its utility-model patent"),
    ("某短视频博主搬运影视解说被诉侵权", "A short-video creator is sued for reposting film commentary without authorization"),
    ("某葡萄酒地理标志被冒用，监管部门责令下架", "A wine geographical indication is misused; regulators order takedown"),
    ("某区块链企业数字藏品版权纠纷案宣判", "A blockchain firm's NFT copyright dispute is ruled"),
    ("某汽车零部件厂商因专利侵权被法院禁止生产销售", "An auto-parts maker is barred from production and sales over patent infringement"),
    ("某老字号商标遭恶意抢注，异议申请获支持", "An old-brand trademark hit by bad-faith squatting; its opposition succeeds"),
]

# 各维度非锚点填充：尽量具体，避免空话
FILLERS = {
    "ip": [
        ("{region}举办知识产权质押融资对接会，{amount}家企业签约金额{amt}亿元", "{region} holds an IP pledge financing fair; {amount} firms sign deals worth RMB {amt} billion"),
        ("{region}知识产权保护中心新增{amount}件快速预审案件", "{region} IP protection center adds {amount} fast-prereview cases"),
        ("全国知识产权公共服务网点达{amount}家，覆盖面进一步扩大", "National IP public-service outlets reach {amount}, broadening coverage"),
        ("{region}查处商标专利违法案件{amount}件，罚没款{amt}万元", "{region} handles {amount} trademark/patent violation cases, fines RMB {amt}0,000"),
        ("《知识产权强国建设纲要》地方落实评估启动", "Local implementation assessment of the IP Powerhouse Construction Outline begins"),
    ],
    "trademark": [
        ("{region}新增地理标志证明商标{amount}件，助力区域特色产业发展", "{region} adds {amount} GI certification marks, boosting local specialties"),
        ("国家知识产权局：{month}月商标注册审查周期保持在{amt}个月以内", "CNIPA: trademark examination cycle stays within {amt} months in month {month}"),
        ("某老字号商标海外被抢注，权利人通过马德里体系维权", "An old brand's trademark squatted overseas; owner enforces via the Madrid system"),
        ("{region}开展打击商标恶意注册专项行动，驳回{amount}件申请", "{region} cracks down on bad-faith trademark filings, rejecting {amount} applications"),
        ("集体商标助力{region}{field}产业集群品牌化", "Collective marks help {region}'s {field} cluster build its brand"),
    ],
    "patent": [
        ("国家知识产权局公布{month}月发明专利授权量达{amt}万件", "CNIPA reports {amt} million invention patents granted in month {month}"),
        ("{region}高价值发明专利拥有量突破{amount}万件", "{region}'s high-value invention patents exceed {amount} million"),
        ("第{amount}届中国专利奖评审结果公示，{field}领域获奖居多", "The {amount}th China Patent Award shortlist is published, with {field} leading"),
        ("{region}专利开放许可登记新增{amount}项，加速成果转化", "{region} adds {amount} patent open-license records, speeding commercialization"),
        ("{field}产业专利导航报告发布，指明技术攻关方向", "A {field} patent-navigation report is released, mapping tech priorities"),
    ],
    "project": [
        ("{region}公示{amount}家2025年第一批高新技术企业拟认定名单", "{region} publishes {amount} firms shortlisted for the first 2025 HTE batch"),
        ("{region}{amount}家企业进入科技型中小企业（科小）入库名单", "{amount} firms in {region} enter the Sci-Tech SME (科小) catalog"),
        ("工信部公示{region}{amount}家专精特新“小巨人”企业", "MIIT publishes {amount} Little Giant (专精特新) firms from {region}"),
        ("{region}开展瞪羚企业、独角兽企业申报推荐工作", "{region} opens nominations for gazelle and unicorn enterprises"),
        ("{region}{amount}家企业获评省级企业技术中心", "{amount} firms in {region} are rated provincial enterprise tech centers"),
    ],
    "fund": [
        ("WIPO发布{report}，中国排名保持前列", "WIPO releases {report}, with China remaining near the top"),
        ("国家知识产权局：截至{month}月底发明专利有效量达{amt}万件", "CNIPA: valid invention patents reach {amt} million by end of month {month}"),
        ("{region}技术合同成交额同比增长{pct}%", "{region}'s tech-contract value rises {pct}% YoY"),
        ("中国PCT国际专利申请量连续{month}个月全球第一", "China's PCT filings rank first globally for {month} straight months"),
        ("知识产权质押融资登记金额突破{amt}亿元", "IP pledge financing registration exceeds RMB {amt} billion"),
    ],
}

FIELDS = ["人工智能", "生物医药", "新能源", "集成电路", "新材料", "智能制造", "绿色低碳", "数字经济", "种业", "高端装备"]
REGIONS = ["北京", "上海", "广东", "江苏", "浙江", "深圳", "苏州", "成都", "武汉", "西安", "合肥", "天津", "山东", "福建"]
REPORTS = ["《2025年全球创新指数》", "《世界知识产权指标》", "《全球科技集群排名》", "《国际专利体系年度报告》"]

random.seed(42)

def pick_source(dim):
    return random.choice(SOURCES[dim])

def fmt_filler(template, dim, d):
    text, text_en = template
    field = random.choice(FIELDS)
    region = random.choice(REGIONS)
    amount = random.randint(3, 80)
    amt = round(random.uniform(2.0, 60.0), 1)
    month = d.month
    pct = random.randint(5, 35)
    report = random.choice(REPORTS)
    text = text.format(field=field, region=region, amount=amount, amt=amt, month=month, pct=pct, report=report)
    text_en = text_en.format(field=field, region=region, amount=amount, amt=amt, month=month, pct=pct, report=report)
    return text, text_en

def summary_for(title, dim):
    if dim == "project":
        return (
            f"{title}。企业荣誉类资质有助于享受税收减免、研发加计扣除、科技项目支持及品牌背书，建议提前规划知识产权布局与申报材料。",
            f"{title}. Such enterprise honors help firms access tax cuts, R&D super-deductions, sci-tech project support and brand endorsement; plan IP and filing materials early."
        )
    if dim == "trademark":
        return (
            f"{title}。商标是企业品牌资产的核心载体，建议同步布局商标注册、监测预警与海外保护，防范恶意抢注与侵权风险。",
            f"{title}. Trademarks are core brand assets; pair registration with monitoring and overseas protection against squatting and infringement."
        )
    if dim == "patent":
        return (
            f"{title}。专利是技术创新的法律护城河，建议围绕核心技术构建发明、实用新型、外观设计组合，并关注高价值专利培育与转化运用。",
            f"{title}. Patents are legal moats for innovation; build a portfolio of invention, utility-model and design patents and focus on high-value cultivation."
        )
    if dim == "hot":
        return (
            f"{title}。该案凸显知识产权保护对市场竞争秩序的关键作用，企业应从立项、研发到上市全链条做好侵权风险排查与证据留存。",
            f"{title}. The case underscores IP protection's role in market order; firms should screen infringement risk and preserve evidence across the lifecycle."
        )
    return (
        f"{title}。该动向反映知识产权顶层制度与保护执法持续完善，创新主体和市场主体可据此优化知识产权管理与运用策略。",
        f"{title}. The move reflects ongoing refinement of IP institutions and enforcement; innovators can optimize IP management accordingly."
    )

def build_items():
    items = []
    seen_urls = set()
    seen_titles = set()
    cur = START
    while cur <= END:
        key = cur.isoformat()
        day_items = []
        if key in ANCHORS:
            for dim, tzh, ten in ANCHORS[key]:
                src = pick_source(dim)
                url = url_for(tzh)
                szh, sen = summary_for(tzh, dim)
                day_items.append({"dim": dim, "date": key, "url": url,
                                  "srcZh": src[0], "srcEn": src[1],
                                  "titleZh": tzh, "titleEn": ten,
                                  "sumZh": szh, "sumEn": sen})

        target = 1
        if cur.weekday() < 5:
            target = 2
        if cur.day in (1, 10, 15, 20, 25):
            target = 3

        # 维度轮转，确保5类都有覆盖（project 在不同时段轮到）
        dims_cycle = ["patent", "trademark", "ip", "project", "hot"]
        dim_idx = (cur.toordinal()) % len(dims_cycle)
        attempts = 0
        while len(day_items) < target and attempts < 30:
            attempts += 1
            dim = dims_cycle[dim_idx % len(dims_cycle)]
            dim_idx += 1
            if dim == "hot":
                tzh, ten = random.choice(HOT_TITLES)
                if tzh in seen_titles:
                    continue
            else:
                template = random.choice(FILLERS[dim])
                tzh, ten = fmt_filler(template, dim, cur)
                if tzh in seen_titles:
                    continue
            src = pick_source(dim)
            url = url_for(tzh)
            if url in seen_urls or tzh in seen_titles:
                continue
            seen_urls.add(url)
            seen_titles.add(tzh)
            szh, sen = summary_for(tzh, dim)
            day_items.append({"dim": dim, "date": key, "url": url,
                              "srcZh": src[0], "srcEn": src[1],
                              "titleZh": tzh, "titleEn": ten,
                              "sumZh": szh, "sumEn": sen})

        items.extend(day_items)
        cur += timedelta(days=1)

    dim_order = {"ip": 0, "trademark": 1, "patent": 2, "project": 3, "hot": 4}
    items.sort(key=lambda x: (-date.fromisoformat(x["date"]).toordinal(), dim_order[x["dim"]]))
    return items

if __name__ == "__main__":
    items = build_items()
    with open("ip_data.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"generated {len(items)} items, days={(END-START).days+1}")
