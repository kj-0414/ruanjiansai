# 六大行业能力树模板配置

INDUSTRIES = [
    "互联网/科技",
    "金融/投资",
    "教育/培训",
    "医疗/健康",
    "制造/工程",
    "销售/市场"
]

# 行业能力树模板
INDUSTRY_TEMPLATES = {
    "互联网/科技": {
        "name": "个人能力",
        "children": [
            {
                "name": "专业技能",
                "weight": 0.4,
                "match_type": "semantic",
                "children": [
                    {"name": "前端技术", "children": []},
                    {"name": "后端技术", "children": []},
                    {"name": "数据库", "children": []},
                    {"name": "工具技能", "children": []}
                ]
            },
            {
                "name": "证书资质",
                "weight": 0.15,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "工作经历",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "项目经历",
                "weight": 0.25,
                "match_type": "semantic",
                children: []
            }
        ]
    },
    "金融/投资": {
        "name": "个人能力",
        "children": [
            {
                "name": "专业资质",
                "weight": 0.3,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "分析能力",
                "weight": 0.3,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "从业经历",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "业绩成果",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            }
        ]
    },
    "教育/培训": {
        "name": "个人能力",
        "children": [
            {
                "name": "教学能力",
                "weight": 0.35,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "证书资质",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "教学成果",
                "weight": 0.25,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "工作经历",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            }
        ]
    },
    "医疗/健康": {
        "name": "个人能力",
        "children": [
            {
                "name": "专业资质",
                "weight": 0.35,
                "match_type": "exact",
                "children": []
            },
            {
                "name": "专业知识",
                "weight": 0.25,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "临床经验",
                "weight": 0.25,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "学术成果",
                "weight": 0.15,
                "match_type": "semantic",
                "children": []
            }
        ]
    },
    "制造/工程": {
        "name": "个人能力",
        "children": [
            {
                "name": "专业技能",
                "weight": 0.35,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "资质证书",
                "weight": 0.2,
                "match_type": "exact",
                "children": []
            },
            {
                "name": "项目经验",
                "weight": 0.25,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "工作经历",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            }
        ]
    },
    "销售/市场": {
        "name": "个人能力",
        "children": [
            {
                "name": "销售能力",
                "weight": 0.3,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "业绩成果",
                "weight": 0.3,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "客户资源",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            },
            {
                "name": "市场洞察",
                "weight": 0.2,
                "match_type": "semantic",
                "children": []
            }
        ]
    }
}

# 行业关键词（用于自动识别）
INDUSTRY_KEYWORDS = {
    "互联网/科技": ["编程", "开发", "前端", "后端", "算法", "人工智能", "数据", "软件", "技术"],
    "金融/投资": ["金融", "投资", "银行", "证券", "基金", "CFA", "CPA", "理财"],
    "教育/培训": ["教师", "教学", "培训", "课程", "学校", "学历", "教育"],
    "医疗/健康": ["医生", "护士", "医疗", "医院", "医学", "临床", "药学"],
    "制造/工程": ["工程师", "机械", "制造", "设计", "施工", "设备", "工艺"],
    "销售/市场": ["销售", "市场", "客户", "营销", "业务", "渠道", "推广"]
}

# 有价值的证书列表（按行业分类）
VALUABLE_CERTIFICATES = {
    "互联网/科技": ["PMP", "AWS", "Azure", "GCP", "软件设计师", "系统架构师"],
    "金融/投资": ["CFA", "CPA", "FRM", "证券从业资格", "基金从业资格"],
    "教育/培训": ["教师资格证", "普通话等级", "心理咨询师"],
    "医疗/健康": ["执业医师", "护士资格证", "药师资格证", "营养师"],
    "制造/工程": ["注册工程师", "建造师", "安全工程师", "质量工程师"],
    "销售/市场": ["市场营销经理", "销售管理师", "客户关系管理师"]
}

def get_industry_template(industry_name: str):
    """获取指定行业的能力树模板"""
    return INDUSTRY_TEMPLATES.get(industry_name, INDUSTRY_TEMPLATES["互联网/科技"])

def identify_industry_by_keywords(text: str) -> str:
    """根据关键词识别行业"""
    text_lower = text.lower()
    scores = {}
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum([1 for keyword in keywords if keyword.lower() in text_lower])
        scores[industry] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "互联网/科技"

def get_valuable_certificates(industry_name: str) -> list:
    """获取指定行业的有价值证书列表"""
    return VALUABLE_CERTIFICATES.get(industry_name, [])
