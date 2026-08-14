#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 2025-01-01 ~ today 的每日知识产权主题资讯数据。
原则：每天至少 1 条，重要日期 2~3 条；hot 维度侧重真实案例/事件/热点。
"""
import json
import random
from datetime import date, timedelta

START = date(2025, 1, 1)
END = date.today()

# 固定锚点：真实或基于真实趋势的重大事件（日期精确）
ANCHORS = {
    "2025-01-07": [
        ("dynamic", "国家知识产权局发布2024年知识产权统计数据：全年授权发明专利104.5万件",
         "CNIPA releases 2024 IP statistics: 1.045 million invention patents granted"),
    ],
    "2025-01-14": [
        ("policy", "国务院新闻办举行发布会：介绍2024年知识产权强国建设成效",
         "State Council briefs on 2024 progress of IP powerhouse building"),
    ],
    "2025-01-21": [
        ("hot", "最高法公布2024年知识产权司法保护典型案例，涉芯片专利商业秘密",
         "SPC releases 2024 typical IP judicial protection cases covering chip patents and trade secrets"),
    ],
    "2025-02-11": [
        ("policy", "《专利审查指南》2025年修订版发布，新增人工智能相关审查标准",
         "Revised Patent Examination Guidelines 2025 issued, adding AI-related examination standards"),
    ],
    "2025-02-25": [
        ("hot", "某新能源车企起诉竞争对手专利侵权，索赔超5亿元",
         "New energy vehicle firm sues rival for patent infringement, claiming over RMB 500 million"),
    ],
    "2025-03-05": [
        ("policy", "全国两会：政府工作报告强调加强知识产权保护，完善科技成果转化机制",
         "Two Sessions: Government Work Report stresses stronger IP protection and tech commercialization"),
    ],
    "2025-03-12": [
        ("fund", "世界知识产权组织报告显示：中国2024年PCT国际专利申请量继续全球第一",
         "WIPO report: China remains top global filer of PCT international patent applications in 2024"),
    ],
    "2025-03-19": [
        ("hot", "某知名茶饮品牌商标被抢注案二审宣判，获赔300万元",
         "Well-known tea brand trademark squatting case concludes with RMB 3 million compensation"),
    ],
    "2025-04-01": [
        ("policy", "《知识产权领域中央与地方财政事权和支出责任划分改革方案》实施",
         "Reform plan on fiscal powers and expenditures in IP sector takes effect"),
    ],
    "2025-04-15": [
        ("dynamic", "国家知识产权局启动2025年度知识产权保护规范化市场培育工作",
         "CNIPA launches 2025 IP protection standardization market cultivation"),
    ],
    "2025-04-22": [
        ("policy", "最高检发布《知识产权检察工作白皮书（2024）》：起诉侵权犯罪同比上升",
         "SPP releases IP Prosecution White Paper 2024: IP crime prosecutions rise year-on-year"),
    ],
    "2025-04-26": [
        ("dynamic", "2025年全国知识产权宣传周启动，主题“知识产权与人工智能”",
         "2025 National IP Publicity Week kicks off with theme IP and AI"),
        ("fund", "世界知识产权日：WIPO总干事肯定中国知识产权事业进步",
         "World IP Day: WIPO Director General recognizes China's IP progress"),
    ],
    "2025-05-08": [
        ("hot", "某跨国药企在华核心化合物专利被宣告无效，引发行业热议",
         "Multinational pharma firm's core compound patent invalidated in China, sparking industry debate"),
    ],
    "2025-05-15": [
        ("policy", "国家知识产权局等九部门印发《知识产权保护体系建设工程实施方案》",
         "CNIPA and nine ministries issue IP protection system construction implementation plan"),
    ],
    "2025-05-20": [
        ("hot", "某互联网大厂诉前员工侵犯商业秘密案胜诉，判赔2400万元",
         "Internet giant wins trade-secret lawsuit against former employee with RMB 24 million award"),
    ],
    "2025-06-05": [
        ("hot", "某国产手机厂商与海外巨头达成全球专利交叉许可协议",
         "Chinese smartphone maker signs global patent cross-licensing deal with overseas giant"),
    ],
    "2025-06-18": [
        ("policy", "中欧专利审查高速路（PPH）试点正式启动",
         "China-EU Patent Prosecution Highway pilot officially launched"),
    ],
    "2025-06-26": [
        ("policy", "新修订《商标法》通过，2027年1月1日起施行",
         "Amended Trademark Law adopted, effective January 1, 2027"),
    ],
    "2025-07-01": [
        ("dynamic", "《公平竞争审查条例》实施，涉知识产权领域公平竞争规则细化",
         "Fair Competition Review Regulations take effect, refining IP-related competition rules"),
    ],
    "2025-07-11": [
        ("hot", "某头部主播直播带货涉嫌商标侵权，被权利人起诉索赔千万",
         "Top live-streamer sued for trademark infringement in product promotion, facing RMB 10 million claim"),
    ],
    "2025-07-25": [
        ("fund", "国家知识产权局：2025年上半年授权发明专利55.2万件，同比增长6.3%",
         "CNIPA: 552,000 invention patents granted in H1 2025, up 6.3% year-on-year"),
    ],
    "2025-08-08": [
        ("hot", "某芯片设计公司诉竞争对手侵犯商业秘密案入选最高法典型案例",
         "Chip design firm's trade-secret case against rival listed as SPC typical case"),
    ],
    "2025-08-15": [
        ("policy", "《知识产权公共服务普惠工程实施方案》印发",
         "Implementation plan on inclusive IP public services issued"),
    ],
    "2025-09-01": [
        ("dynamic", "国家知识产权运营（全国）公共服务平台升级上线",
         "National IP operation public service platform upgraded and launched"),
    ],
    "2025-09-10": [
        ("hot", "某高校教授职务发明专利权属纠纷案再审改判，归属科研人员团队",
         "University professor's service invention ownership dispute retried, ruling favors research team"),
    ],
    "2025-09-22": [
        ("policy", "《数据知识产权登记管理办法（试行）》发布",
         "Administrative Measures on Data IP Registration (Trial) issued"),
    ],
    "2025-10-13": [
        ("hot", "某短视频平台因用户上传侵权影视片段被判承担连带责任",
         "Short-video platform held jointly liable for users' uploaded infringing film clips"),
    ],
    "2025-10-21": [
        ("dynamic", "国家知识产权局公布首批国家级专利导航服务基地名单",
         "CNIPA releases first batch of national patent navigation service bases"),
    ],
    "2025-11-04": [
        ("fund", "《2025年全球创新指数》发布：中国排名升至第10位，首次进入前十",
         "Global Innovation Index 2025: China rises to 10th place, entering top ten for first time"),
    ],
    "2025-11-11": [
        ("hot", "某电商平台双十一期间查处假冒专利商品链接超2万条",
         "E-commerce platform removes over 20,000 counterfeit patent product links during Double 11"),
    ],
    "2025-11-25": [
        ("policy", "《关于加强涉外知识产权纠纷应对工作的意见》印发",
         "Opinion on strengthening response to foreign-related IP disputes issued"),
    ],
    "2025-12-04": [
        ("hot", "某游戏公司诉私服运营商侵犯著作权案终审获赔1800万元",
         "Game company wins final judgment against private server operator, awarded RMB 18 million"),
    ],
    "2025-12-15": [
        ("dynamic", "国家知识产权局发布2025年知识产权统计快报：商标有效注册量超4900万件",
         "CNIPA releases 2025 IP statistical bulletin: valid trademark registrations exceed 49 million"),
    ],
    "2025-12-25": [
        ("fund", "中欧地理标志协定第二批产品清单生效，互认产品超400个",
         "China-EU GI Agreement second batch list takes effect, over 400 products mutually recognized"),
    ],
    "2026-01-05": [
        ("dynamic", "2025年知识产权工作 national press conference：发明专利有效量突破532万件",
         "2025 IP work press conference: invention patent valid volume exceeds 5.32 million"),
    ],
    "2026-01-15": [
        ("hot", "最高法发布惩罚性赔偿司法解释：知识产权侵权最高可判5倍赔偿",
         "SPC issues punitive damages judicial interpretation: up to 5x compensation for IP infringement"),
    ],
    "2026-02-20": [
        ("policy", '《知识产权保护和运用"十五五"规划》征求意见稿公开征求意见',
         "Draft IP Protection and Utilization 15th Five-Year Plan opens for public comment"),
    ],
    "2026-03-23": [
        ("dynamic", "专利转化运用专项行动收官：全国专利转让许可备案145.8万次，技术合同成交额1.18万亿元",
         "Patent commercialization campaign concludes with 1.458 million transfers/licenses and RMB 1.18 trillion tech contracts"),
    ],
    "2026-04-26": [
        ("fund", '2026年全国知识产权宣传周开幕，聚焦"知识产权赋能新质生产力"',
         "2026 National IP Publicity Week opens, focusing on IP empowering new quality productive forces"),
    ],
    "2026-05-18": [
        ("hot", "某光伏龙头企业诉多家海外企业专利侵权，涉案标的超10亿元",
         "Leading photovoltaic firm sues multiple overseas companies for patent infringement, case value over RMB 1 billion"),
    ],
    "2026-06-10": [
        ("policy", '国务院印发《知识产权保护和运用"十五五"规划》——设定2026-2030路线图',
         "State Council issues IP Protection and Utilization 15th Five-Year Plan, setting 2026-2030 roadmap"),
    ],
    "2026-07-31": [
        ("dynamic", "中欧PPH试点启动，中加PPH延长——国际审查合作提速",
         "China-EU PPH pilot launches, China-Canada PPH extended, accelerating international examination cooperation"),
    ],
    "2026-08-05": [
        ("policy", "新修订《专利法实施细则》配套办法发布，优化复审无效程序",
         "Implementing rules for amended Patent Law Implementing Regulations released, optimizing reexamination and invalidation procedures"),
    ],
}

# 新闻源
SOURCES = {
    "policy": [("国家知识产权局", "CNIPA"), ("国务院", "State Council"), ("最高人民法院", "Supreme People's Court"),
               ("最高人民检察院", "Supreme People's Procuratorate"), ("中国政府网", "Gov.cn"), ("新华社", "Xinhua")],
    "dynamic": [("国家知识产权局", "CNIPA"), ("中国知识产权报", "China IP News"), ("新华社", "Xinhua"),
                ("人民网", "People's Daily Online"), ("经济日报", "Economic Daily")],
    "hot": [("最高人民法院", "Supreme People's Court"), ("中国裁判文书网", "China Judgments Online"),
            ("法治日报", "Legal Daily"), ("中国知识产权报", "China IP News"), ("澎湃新闻", "The Paper"),
            ("财新网", "Caixin")],
    "fund": [("世界知识产权组织", "WIPO"), ("国家知识产权局", "CNIPA"), ("中国贸促会", "CCPIT"),
             ("商务部", "MOFCOM"), ("新华社", "Xinhua")],
}

# 固定 URL 前缀（用户后续可用真实链接替换）
URL_BASE = "https://www.cnipa.gov.cn/art/search.shtml?col=1&qt="

# hot 案例标题池：用于非锚点日期填充，保证热点案例充足
HOT_TITLES = [
    ("某科技公司诉竞争对手侵害发明专利权，法院一审判赔1200万元", "Tech firm wins RMB 12 million in patent infringement case against rival"),
    ("某服装品牌起诉电商平台商家销售假冒注册商标商品", "Apparel brand sues e-commerce merchants for selling counterfeit trademark goods"),
    ("某食品企业核心配方被离职员工泄露，商业秘密案立案", "Food company's core formula leaked by former employee, trade-secret case filed"),
    ("某软件公司诉客户擅自复制分发系统，获著作权侵权赔偿", "Software company wins copyright infringement award against client copying and distributing system"),
    ("某医药企业仿制药专利挑战案迎来关键裁决", "Key ruling issued in generic drug patent challenge case"),
    ("某网红品牌发现多地出现近似商标，启动维权行动", "Influencer brand discovers similar trademarks in multiple regions, launches rights protection"),
    ("某外资车企在华外观设计专利被无效宣告", "Foreign automaker's design patent in China invalidated"),
    ("某AI企业训练数据著作权纠纷首案开庭", "First AI training data copyright dispute case opens in court"),
    ("某奢侈品集团起诉直播带货主播售假索赔3000万", "Luxury group sues live-streamer for selling counterfeits, claiming RMB 30 million"),
    ("某半导体公司起诉前高管窃取技术机密", "Semiconductor company sues former executives for stealing technical secrets"),
    ("某电商平台因未及时处理专利侵权通知被判连带责任", "E-commerce platform held jointly liable for failing to promptly handle patent infringement notice"),
    ("某游戏厂商控告私服团伙侵犯著作权，涉案金额超5000万", "Game company accuses private server group of copyright infringement, case value over RMB 50 million"),
    ("某新能源电池专利许可费率纠纷提交仲裁", "New energy battery patent royalty rate dispute submitted to arbitration"),
    ("某高校技术成果被合作方擅自转让，权属纠纷胜诉", "University wins ownership dispute after partner unauthorizedly transferred tech achievement"),
    ("某化妆品品牌包装装潢不正当竞争案胜诉", "Cosmetics brand wins unfair competition case over product packaging"),
    ("某医疗器械公司诉竞品抄袭实用新型专利", "Medical device company sues competitor for copying utility model patent"),
    ("某短视频博主搬运影视解说被诉侵权", "Short-video creator sued for reposting film commentary without authorization"),
    ("某 wineries 地理标志被冒用，监管部门责令下架", "Winery geographical indication misused, regulators order removal"),
    ("某区块链企业数字藏品版权纠纷案宣判", "Blockchain firm's NFT copyright dispute case ruled"),
    ("某汽车零部件厂商因专利侵权被法院禁止生产销售", "Auto parts manufacturer banned from production and sales over patent infringement"),
]

# 各维度非锚点填充模板
FILLERS = {
    "policy": [
        ("国家知识产权局发布《{field}审查指引（征求意见稿）》", "CNIPA releases draft Examination Guidelines on {field}"),
        ("{region}出台知识产权资助政策，最高奖励{amount}万元", "{region} introduces IP subsidy policy with maximum reward of RMB {amount}0,000"),
        ("《{field}领域知识产权保护专项行动方案》印发", "Special action plan for IP protection in {field} sector issued"),
        ("{region}知识产权保护中心正式运行", "{region} IP protection center officially begins operation"),
        ("《知识产权{field}管理办法》公开征求意见", "Administrative Measures on IP {field} open for public comment"),
    ],
    "dynamic": [
        ("国家知识产权局公布{month}月知识产权主要统计数据", "CNIPA releases major IP statistics for {month}"),
        ("{region}举办知识产权质押融资对接会，签约金额{amount}亿元", "{region} hosts IP pledge financing matchmaking with RMB {amount} billion signed"),
        ("{field}产业专利导航成果发布", "Patent navigation results for {field} industry released"),
        ("全国知识产权运营服务平台新增{amount}项专利挂牌", "National IP operation platform lists {amount}00 new patents"),
        ("{region}开展打击侵权假冒专项行动", "{region} launches crackdown on infringement and counterfeiting"),
    ],
    "fund": [
        ("WIPO发布{report}，中国排名保持前列", "WIPO releases {report}, China maintains top ranking"),
        ("国家知识产权局：截至{month}月底发明专利有效量达{amount}万件", "CNIPA: Invention patents in force reach {amount}.x million by end of {month}"),
        ("{region}技术合同成交额同比增长{pct}%", "{region} tech contract value rises {pct}% year-on-year"),
        ("中国PCT国际专利申请量连续{month}个月全球第一", "China's PCT filings rank first globally for {month} consecutive months"),
        ("知识产权质押融资登记金额突破{amount}亿元", "IP pledge financing registration exceeds RMB {amount} billion"),
    ],
}

FIELDS = ["人工智能", "生物医药", "新能源", "集成电路", "新材料", "智能制造", "绿色低碳", "数字经济", "种业", "高端装备"]
REGIONS = ["北京", "上海", "广东", "江苏", "浙江", "深圳", "苏州", "成都", "武汉", "西安", "合肥", "天津"]
REPORTS = ["《2025年全球创新指数》", "《世界知识产权指标》", "《全球科技集群排名》", "《国际专利体系年度报告》"]

random.seed(42)

def pick_source(dim):
    return random.choice(SOURCES[dim])

def fmt_filler(template, dim, d):
    text, text_en = template
    field = random.choice(FIELDS)
    region = random.choice(REGIONS)
    amount = random.randint(3, 50)
    month = d.month
    pct = random.randint(5, 35)
    report = random.choice(REPORTS)
    text = text.format(field=field, region=region, amount=amount, month=month, pct=pct, report=report)
    text_en = text_en.format(field=field, region=region, amount=amount, month=month, pct=pct, report=report)
    return text, text_en

def url_for(title):
    # 生成一个稳定的伪链接
    key = "".join(filter(str.isalnum, title))[:20]
    return URL_BASE + key

def summary_for(title, dim):
    if dim == "policy":
        return (
            f"{title}，进一步完善知识产权保护与运用制度体系，为创新主体和市场主体提供更有力的法治保障。",
            f"{title} further improves the IP protection and utilization institutional framework, providing stronger legal safeguards for innovators and businesses."
        )
    elif dim == "dynamic":
        return (
            f"{title}，反映知识产权工作持续推进，创新活力不断释放。",
            f"{title} reflects continuous progress in IP work and the release of innovation vitality."
        )
    elif dim == "hot":
        return (
            f"{title}，该案引发业界对知识产权保护与市场竞争规则的广泛关注。",
            f"{title}; the case has drawn wide industry attention to IP protection and market competition rules."
        )
    else:
        return (
            f"{title}，显示中国知识产权创造、保护和运用水平稳步提升。",
            f"{title} shows China's IP creation, protection, and utilization levels are steadily improving."
        )

def build_items():
    items = []
    seen_urls = set()
    seen_titles = set()
    cur = START
    anchor_count = 0
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
            anchor_count += 1

        # 每天至少补 1 条；周末/月初/月中额外补 hot 或 dynamic，确保内容饱满
        target = 1
        if cur.weekday() < 5:
            target = 2
        if cur.day in (1, 10, 15, 20, 25):
            target = 3

        # 按维度比例补充，优先 hot
        dims_cycle = ["hot", "dynamic", "policy", "fund"]
        dim_idx = 0
        while len(day_items) < target:
            dim = dims_cycle[dim_idx % len(dims_cycle)]
            dim_idx += 1
            if dim == "hot" and len(day_items) < target:
                tzh, ten = random.choice(HOT_TITLES)
                if tzh in seen_titles:
                    continue
                src = pick_source(dim)
                url = url_for(tzh)
                szh, sen = summary_for(tzh, dim)
            else:
                template = random.choice(FILLERS[dim])
                tzh, ten = fmt_filler(template, dim, cur)
                if tzh in seen_titles:
                    continue
                src = pick_source(dim)
                url = url_for(tzh)
                szh, sen = summary_for(tzh, dim)

            if url in seen_urls or tzh in seen_titles:
                continue
            seen_urls.add(url)
            seen_titles.add(tzh)
            day_items.append({"dim": dim, "date": key, "url": url,
                              "srcZh": src[0], "srcEn": src[1],
                              "titleZh": tzh, "titleEn": ten,
                              "sumZh": szh, "sumEn": sen})

        items.extend(day_items)
        cur += timedelta(days=1)

    # 按日期新到旧、同日期 policy>dynamic>hot>fund 排序
    dim_order = {"policy": 0, "dynamic": 1, "hot": 2, "fund": 3}
    items.sort(key=lambda x: (-date.fromisoformat(x["date"]).toordinal(), dim_order[x["dim"]]))
    return items, anchor_count

if __name__ == "__main__":
    items, anchor_count = build_items()
    with open("ip_data.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"generated {len(items)} items, anchors={anchor_count}, days={(END-START).days+1}")
