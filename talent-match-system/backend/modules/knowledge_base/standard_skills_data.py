"""
标准技能数据
包含技能ID到名称的映射、分类、别名等信息
基于IT行业常用技能整理
"""

STANDARD_SKILLS = {
    # 编程语言 (0-99)
    0: {"name": "Python", "category": "编程语言", "aliases": ["python", "py", "python3"], "difficulty": 2},
    1: {"name": "Java", "category": "编程语言", "aliases": ["java", "javase", "javaee"], "difficulty": 3},
    2: {"name": "JavaScript", "category": "编程语言", "aliases": ["javascript", "js", "ecmascript", "es6"], "difficulty": 2},
    3: {"name": "TypeScript", "category": "编程语言", "aliases": ["typescript", "ts"], "difficulty": 3},
    4: {"name": "Go", "category": "编程语言", "aliases": ["golang", "go语言"], "difficulty": 3},
    5: {"name": "Rust", "category": "编程语言", "aliases": ["rust", "rust语言"], "difficulty": 5},
    6: {"name": "C++", "category": "编程语言", "aliases": ["cpp", "c++", "c语言"], "difficulty": 4},
    7: {"name": "C#", "category": "编程语言", "aliases": ["csharp", "c#", ".net"], "difficulty": 3},
    8: {"name": "PHP", "category": "编程语言", "aliases": ["php", "php7", "php8"], "difficulty": 2},
    9: {"name": "Ruby", "category": "编程语言", "aliases": ["ruby", "rubyonrails", "rails"], "difficulty": 3},
    10: {"name": "Swift", "category": "编程语言", "aliases": ["swift", "swift语言", "ios开发"], "difficulty": 3},
    11: {"name": "Kotlin", "category": "编程语言", "aliases": ["kotlin", "android开发"], "difficulty": 3},
    12: {"name": "Scala", "category": "编程语言", "aliases": ["scala"], "difficulty": 5},
    13: {"name": "R", "category": "编程语言", "aliases": ["r语言", "rstats"], "difficulty": 3},
    14: {"name": "MATLAB", "category": "编程语言", "aliases": ["matlab", "matlab编程"], "difficulty": 3},
    15: {"name": "Perl", "category": "编程语言", "aliases": ["perl"], "difficulty": 4},
    16: {"name": "Shell", "category": "编程语言", "aliases": ["shell", "bash", "sh", "zsh"], "difficulty": 2},
    17: {"name": "Lua", "category": "编程语言", "aliases": ["lua"], "difficulty": 2},
    18: {"name": "Dart", "category": "编程语言", "aliases": ["dart", "flutter"], "difficulty": 3},
    19: {"name": "Objective-C", "category": "编程语言", "aliases": ["objectivec", "oc", "ios"], "difficulty": 4},
    
    # 前端技术 (100-199)
    100: {"name": "HTML", "category": "前端技术", "aliases": ["html", "html5"], "difficulty": 1},
    101: {"name": "CSS", "category": "前端技术", "aliases": ["css", "css3"], "difficulty": 2},
    102: {"name": "React", "category": "前端技术", "aliases": ["react", "reactjs", "react.js", "reactnative"], "difficulty": 3},
    103: {"name": "Vue.js", "category": "前端技术", "aliases": ["vue", "vuejs", "vue.js", "vue3"], "difficulty": 2},
    104: {"name": "Angular", "category": "前端技术", "aliases": ["angular", "angularjs", "angular.js"], "difficulty": 4},
    105: {"name": "Node.js", "category": "前端技术", "aliases": ["node", "nodejs", "node.js"], "difficulty": 3},
    106: {"name": "jQuery", "category": "前端技术", "aliases": ["jquery", "jq"], "difficulty": 2},
    107: {"name": "Webpack", "category": "前端技术", "aliases": ["webpack"], "difficulty": 3},
    108: {"name": "Vite", "category": "前端技术", "aliases": ["vite"], "difficulty": 2},
    109: {"name": "SASS", "category": "前端技术", "aliases": ["sass", "scss"], "difficulty": 2},
    110: {"name": "LESS", "category": "前端技术", "aliases": ["less"], "difficulty": 2},
    111: {"name": "Bootstrap", "category": "前端技术", "aliases": ["bootstrap", "bs"], "difficulty": 2},
    112: {"name": "Tailwind CSS", "category": "前端技术", "aliases": ["tailwind", "tailwindcss"], "difficulty": 3},
    113: {"name": "Next.js", "category": "前端技术", "aliases": ["nextjs", "next.js"], "difficulty": 4},
    114: {"name": "Nuxt.js", "category": "前端技术", "aliases": ["nuxtjs", "nuxt.js"], "difficulty": 4},
    115: {"name": "React Native", "category": "前端技术", "aliases": ["reactnative", "rn"], "difficulty": 4},
    116: {"name": "Flutter", "category": "前端技术", "aliases": ["flutter"], "difficulty": 4},
    117: {"name": "Electron", "category": "前端技术", "aliases": ["electron"], "difficulty": 4},
    118: {"name": "TypeScript", "category": "前端技术", "aliases": ["typescript", "ts"], "difficulty": 3},
    
    # 后端框架 (200-299)
    200: {"name": "Spring", "category": "后端框架", "aliases": ["spring", "springframework"], "difficulty": 4},
    201: {"name": "Spring Boot", "category": "后端框架", "aliases": ["springboot", "spring-boot"], "difficulty": 3},
    202: {"name": "Django", "category": "后端框架", "aliases": ["django", "django框架"], "difficulty": 3},
    203: {"name": "Flask", "category": "后端框架", "aliases": ["flask", "flask框架"], "difficulty": 2},
    204: {"name": "FastAPI", "category": "后端框架", "aliases": ["fastapi"], "difficulty": 3},
    205: {"name": "Express", "category": "后端框架", "aliases": ["express", "expressjs"], "difficulty": 2},
    206: {"name": "NestJS", "category": "后端框架", "aliases": ["nestjs", "nest.js"], "difficulty": 4},
    207: {"name": "Koa", "category": "后端框架", "aliases": ["koa", "koajs"], "difficulty": 3},
    208: {"name": "Laravel", "category": "后端框架", "aliases": ["laravel", "php框架"], "difficulty": 3},
    209: {"name": "Ruby on Rails", "category": "后端框架", "aliases": ["rails", "ror"], "difficulty": 3},
    210: {"name": "Gin", "category": "后端框架", "aliases": ["gin", "go框架"], "difficulty": 3},
    211: {"name": "Echo", "category": "后端框架", "aliases": ["echo", "go框架"], "difficulty": 3},
    212: {"name": "Fiber", "category": "后端框架", "aliases": ["fiber", "go框架"], "difficulty": 3},
    213: {"name": "Spring Cloud", "category": "后端框架", "aliases": ["springcloud", "微服务"], "difficulty": 5},
    214: {"name": "MyBatis", "category": "后端框架", "aliases": ["mybatis"], "difficulty": 3},
    215: {"name": "Hibernate", "category": "后端框架", "aliases": ["hibernate", "orm"], "difficulty": 4},
    
    # 数据库 (300-399)
    300: {"name": "MySQL", "category": "数据库", "aliases": ["mysql", "mysql数据库"], "difficulty": 2},
    301: {"name": "PostgreSQL", "category": "数据库", "aliases": ["postgresql", "postgres", "pg"], "difficulty": 3},
    302: {"name": "MongoDB", "category": "数据库", "aliases": ["mongodb", "mongo", "nosql"], "difficulty": 2},
    303: {"name": "Redis", "category": "数据库", "aliases": ["redis", "redis缓存"], "difficulty": 3},
    304: {"name": "Oracle", "category": "数据库", "aliases": ["oracle", "oracle数据库"], "difficulty": 3},
    305: {"name": "SQL Server", "category": "数据库", "aliases": ["sqlserver", "mssql", "ms-sql"], "difficulty": 3},
    306: {"name": "SQLite", "category": "数据库", "aliases": ["sqlite", "轻量级数据库"], "difficulty": 1},
    307: {"name": "Elasticsearch", "category": "数据库", "aliases": ["elasticsearch", "es", "搜索"], "difficulty": 4},
    308: {"name": "Cassandra", "category": "数据库", "aliases": ["cassandra"], "difficulty": 4},
    309: {"name": "DynamoDB", "category": "数据库", "aliases": ["dynamodb", "aws数据库"], "difficulty": 4},
    310: {"name": "Neo4j", "category": "数据库", "aliases": ["neo4j", "图数据库"], "difficulty": 4},
    311: {"name": "HBase", "category": "数据库", "aliases": ["hbase", "hadoop数据库"], "difficulty": 4},
    312: {"name": "ClickHouse", "category": "数据库", "aliases": ["clickhouse", "列式数据库"], "difficulty": 4},
    313: {"name": "达梦", "category": "数据库", "aliases": ["dm", "dameng", "国产数据库"], "difficulty": 3},
    314: {"name": "TiDB", "category": "数据库", "aliases": ["tidb", "分布式数据库"], "difficulty": 4},
    
    # 大数据 (400-499)
    400: {"name": "Hadoop", "category": "大数据", "aliases": ["hadoop", "大数据框架"], "difficulty": 4},
    401: {"name": "Spark", "category": "大数据", "aliases": ["spark", "spark大数据"], "difficulty": 4},
    402: {"name": "Hive", "category": "大数据", "aliases": ["hive", "数据仓库"], "difficulty": 3},
    403: {"name": "Kafka", "category": "大数据", "aliases": ["kafka", "消息队列", "mq"], "difficulty": 4},
    404: {"name": "Flink", "category": "大数据", "aliases": ["flink", "流处理"], "difficulty": 5},
    405: {"name": "Storm", "category": "大数据", "aliases": ["storm", "流处理"], "difficulty": 4},
    406: {"name": "HDFS", "category": "大数据", "aliases": ["hdfs", "分布式文件系统"], "difficulty": 3},
    407: {"name": "MapReduce", "category": "大数据", "aliases": ["mapreduce", "分布式计算"], "difficulty": 3},
    408: {"name": "Zookeeper", "category": "大数据", "aliases": ["zookeeper", "zk"], "difficulty": 3},
    409: {"name": "Kylin", "category": "大数据", "aliases": ["kylin", "olap"], "difficulty": 4},
    410: {"name": "Presto", "category": "大数据", "aliases": ["presto", "查询引擎"], "difficulty": 4},
    411: {"name": "Doris", "category": "大数据", "aliases": ["doris", "分析数据库"], "difficulty": 4},
    
    # 机器学习/AI (500-599)
    500: {"name": "TensorFlow", "category": "机器学习/AI", "aliases": ["tensorflow", "tf", "深度学习框架"], "difficulty": 4},
    501: {"name": "PyTorch", "category": "机器学习/AI", "aliases": ["pytorch", "torch", "深度学习框架"], "difficulty": 4},
    502: {"name": "Keras", "category": "机器学习/AI", "aliases": ["keras", "深度学习"], "difficulty": 3},
    503: {"name": "Scikit-learn", "category": "机器学习/AI", "aliases": ["scikit-learn", "sklearn", "机器学习"], "difficulty": 3},
    504: {"name": "XGBoost", "category": "机器学习/AI", "aliases": ["xgboost", "梯度提升"], "difficulty": 4},
    505: {"name": "LightGBM", "category": "机器学习/AI", "aliases": ["lightgbm", "梯度提升"], "difficulty": 4},
    506: {"name": "Machine Learning", "category": "机器学习/AI", "aliases": ["ml", "机器学习", "machinelearning"], "difficulty": 3},
    507: {"name": "Deep Learning", "category": "机器学习/AI", "aliases": ["dl", "深度学习", "deeplearning"], "difficulty": 4},
    508: {"name": "NLP", "category": "机器学习/AI", "aliases": ["nlp", "自然语言处理", "naturallanguageprocessing"], "difficulty": 4},
    509: {"name": "Computer Vision", "category": "机器学习/AI", "aliases": ["cv", "计算机视觉", "computervision"], "difficulty": 4},
    510: {"name": "Pandas", "category": "机器学习/AI", "aliases": ["pandas", "数据分析"], "difficulty": 2},
    511: {"name": "NumPy", "category": "机器学习/AI", "aliases": ["numpy", "数值计算"], "difficulty": 2},
    512: {"name": "OpenCV", "category": "机器学习/AI", "aliases": ["opencv", "图像处理"], "difficulty": 3},
    513: {"name": "LangChain", "category": "机器学习/AI", "aliases": ["langchain", "llm应用"], "difficulty": 5},
    514: {"name": "Hugging Face", "category": "机器学习/AI", "aliases": ["huggingface", "transformers", "nlp"], "difficulty": 4},
    
    # DevOps/云计算 (600-699)
    600: {"name": "Docker", "category": "DevOps/云计算", "aliases": ["docker", "容器", "容器化"], "difficulty": 2},
    601: {"name": "Kubernetes", "category": "DevOps/云计算", "aliases": ["kubernetes", "k8s", "k8s容器编排"], "difficulty": 5},
    602: {"name": "Jenkins", "category": "DevOps/云计算", "aliases": ["jenkins", "ci/cd", "持续集成"], "difficulty": 3},
    603: {"name": "GitLab CI", "category": "DevOps/云计算", "aliases": ["gitlab-ci", "ci/cd"], "difficulty": 3},
    604: {"name": "GitHub Actions", "category": "DevOps/云计算", "aliases": ["github-actions", "ci/cd"], "difficulty": 3},
    605: {"name": "Ansible", "category": "DevOps/云计算", "aliases": ["ansible", "自动化运维"], "difficulty": 3},
    606: {"name": "Terraform", "category": "DevOps/云计算", "aliases": ["terraform", "iac", "基础设施"], "difficulty": 4},
    607: {"name": "Prometheus", "category": "DevOps/云计算", "aliases": ["prometheus", "监控"], "difficulty": 3},
    608: {"name": "Grafana", "category": "DevOps/云计算", "aliases": ["grafana", "可视化监控"], "difficulty": 2},
    609: {"name": "Nginx", "category": "DevOps/云计算", "aliases": ["nginx", "反向代理", "web服务器"], "difficulty": 2},
    610: {"name": "Apache", "category": "DevOps/云计算", "aliases": ["apache", "httpd", "web服务器"], "difficulty": 2},
    611: {"name": "Tomcat", "category": "DevOps/云计算", "aliases": ["tomcat", "java容器"], "difficulty": 2},
    612: {"name": "Linux", "category": "DevOps/云计算", "aliases": ["linux", "linux系统"], "difficulty": 3},
    613: {"name": "Shell Scripting", "category": "DevOps/云计算", "aliases": ["shell", "bash", "脚本"], "difficulty": 2},
    614: {"name": "Helm", "category": "DevOps/云计算", "aliases": ["helm", "k8s包管理"], "difficulty": 3},
    615: {"name": "Istio", "category": "DevOps/云计算", "aliases": ["istio", "服务网格"], "difficulty": 5},
    
    # 云服务 (700-799)
    700: {"name": "AWS", "category": "云服务", "aliases": ["aws", "amazonwebservices", "亚马逊云"], "difficulty": 4},
    701: {"name": "Azure", "category": "云服务", "aliases": ["azure", "microsoftazure", "微软云"], "difficulty": 4},
    702: {"name": "GCP", "category": "云服务", "aliases": ["gcp", "googlecloud", "谷歌云"], "difficulty": 4},
    703: {"name": "阿里云", "category": "云服务", "aliases": ["aliyun", "阿里巴巴云"], "difficulty": 3},
    704: {"name": "腾讯云", "category": "云服务", "aliases": ["tencentcloud", "腾讯云计算"], "difficulty": 3},
    705: {"name": "华为云", "category": "云服务", "aliases": ["huaweicloud", "华为云计算"], "difficulty": 3},
    706: {"name": "Docker Swarm", "category": "云服务", "aliases": ["dockerswarm", "容器编排"], "difficulty": 3},
    707: {"name": "ECS", "category": "云服务", "aliases": ["ecs", "弹性计算"], "difficulty": 2},
    708: {"name": "S3", "category": "云服务", "aliases": ["s3", "对象存储"], "difficulty": 2},
    709: {"name": "Lambda", "category": "云服务", "aliases": ["lambda", "serverless", "无服务器"], "difficulty": 4},
    710: {"name": "容器服务", "category": "云服务", "aliases": ["eks", "aks", "gke", "容器托管"], "difficulty": 4},
    
    # 版本控制/协作 (800-899)
    800: {"name": "Git", "category": "版本控制/协作", "aliases": ["git", "版本控制", "代码管理"], "difficulty": 2},
    801: {"name": "GitHub", "category": "版本控制/协作", "aliases": ["github", "代码托管"], "difficulty": 2},
    802: {"name": "GitLab", "category": "版本控制/协作", "aliases": ["gitlab", "devops平台"], "difficulty": 2},
    803: {"name": "SVN", "category": "版本控制/协作", "aliases": ["svn", "subversion"], "difficulty": 2},
    804: {"name": "Jira", "category": "版本控制/协作", "aliases": ["jira", "项目管理"], "difficulty": 2},
    805: {"name": "Confluence", "category": "版本控制/协作", "aliases": ["confluence", "文档协作"], "difficulty": 2},
    806: {"name": "Slack", "category": "版本控制/协作", "aliases": ["slack", "团队协作"], "difficulty": 1},
    807: {"name": "Notion", "category": "版本控制/协作", "aliases": ["notion", "知识管理"], "difficulty": 1},
    
    # 移动开发 (900-999)
    900: {"name": "Android", "category": "移动开发", "aliases": ["android", "安卓", "android开发"], "difficulty": 3},
    901: {"name": "iOS", "category": "移动开发", "aliases": ["ios", "苹果开发", "iphone开发"], "difficulty": 3},
    902: {"name": "React Native", "category": "移动开发", "aliases": ["reactnative", "rn", "跨平台"], "difficulty": 4},
    903: {"name": "Flutter", "category": "移动开发", "aliases": ["flutter", "跨平台"], "difficulty": 4},
    904: {"name": "uni-app", "category": "移动开发", "aliases": ["uniapp", "小程序"], "difficulty": 3},
    905: {"name": "微信小程序", "category": "移动开发", "aliases": ["wechat", "miniprogram", "小程序开发"], "difficulty": 2},
    906: {"name": "SwiftUI", "category": "移动开发", "aliases": ["swiftui", "ios ui"], "difficulty": 4},
    907: {"name": "Jetpack Compose", "category": "移动开发", "aliases": ["compose", "android ui"], "difficulty": 4},
    
    # 测试 (1000-1099)
    1000: {"name": "Selenium", "category": "测试", "aliases": ["selenium", "ui自动化"], "difficulty": 3},
    1001: {"name": "JUnit", "category": "测试", "aliases": ["junit", "java单元测试"], "difficulty": 2},
    1002: {"name": "Pytest", "category": "测试", "aliases": ["pytest", "python测试"], "difficulty": 2},
    1003: {"name": "Postman", "category": "测试", "aliases": ["postman", "api测试"], "difficulty": 1},
    1004: {"name": "JMeter", "category": "测试", "aliases": ["jmeter", "性能测试"], "difficulty": 3},
    1005: {"name": "Appium", "category": "测试", "aliases": ["appium", "移动端测试"], "difficulty": 3},
    1006: {"name": "Cypress", "category": "测试", "aliases": ["cypress", "前端测试"], "difficulty": 3},
    1007: {"name": "Jest", "category": "测试", "aliases": ["jest", "javascript测试"], "difficulty": 2},
    1008: {"name": "Mocha", "category": "测试", "aliases": ["mocha", "javascript测试框架"], "difficulty": 2},
    
    # 安全 (1100-1199)
    1100: {"name": "网络安全", "category": "安全", "aliases": ["networksecurity", "网络安全"], "difficulty": 4},
    1101: {"name": "Web安全", "category": "安全", "aliases": ["websecurity", "xss", "csrf"], "difficulty": 3},
    1102: {"name": "渗透测试", "category": "安全", "aliases": ["pentest", "penetration", "黑客"], "difficulty": 5},
    1103: {"name": "密码学", "category": "安全", "aliases": ["cryptography", "加密"], "difficulty": 4},
    1104: {"name": "OAuth", "category": "安全", "aliases": ["oauth", "身份认证"], "difficulty": 3},
    1105: {"name": "JWT", "category": "安全", "aliases": ["jwt", "token认证"], "difficulty": 3},
    1106: {"name": "SSL/TLS", "category": "安全", "aliases": ["ssl", "tls", "证书"], "difficulty": 3},
    
    # 网络/协议 (1200-1299)
    1200: {"name": "HTTP/HTTPS", "category": "网络/协议", "aliases": ["http", "https", "网络协议"], "difficulty": 2},
    1201: {"name": "TCP/IP", "category": "网络/协议", "aliases": ["tcp", "ip", "网络协议"], "difficulty": 3},
    1202: {"name": "DNS", "category": "网络/协议", "aliases": ["dns", "域名解析"], "difficulty": 2},
    1203: {"name": "WebSocket", "category": "网络/协议", "aliases": ["websocket", "实时通信"], "difficulty": 3},
    1204: {"name": "RESTful API", "category": "网络/协议", "aliases": ["rest", "restful", "api设计"], "difficulty": 2},
    1205: {"name": "GraphQL", "category": "网络/协议", "aliases": ["graphql", "api查询语言"], "difficulty": 3},
    1206: {"name": "gRPC", "category": "网络/协议", "aliases": ["grpc", "rpc框架"], "difficulty": 4},
    1207: {"name": "MQTT", "category": "网络/协议", "aliases": ["mqtt", "物联网协议"], "difficulty": 3},
    1208: {"name": "CDN", "category": "网络/协议", "aliases": ["cdn", "内容分发"], "difficulty": 2},
    1209: {"name": "负载均衡", "category": "网络/协议", "aliases": ["loadbalancing", "lb", "nginx"], "difficulty": 3},
    
    # 软件工程/方法论 (1300-1399)
    1300: {"name": "敏捷开发", "category": "软件工程/方法论", "aliases": ["agile", "scrum", "看板"], "difficulty": 2},
    1301: {"name": "DevOps", "category": "软件工程/方法论", "aliases": ["devops", "开发运维"], "difficulty": 3},
    1302: {"name": "CI/CD", "category": "软件工程/方法论", "aliases": ["cicd", "持续集成", "持续部署"], "difficulty": 3},
    1303: {"name": "微服务", "category": "软件工程/方法论", "aliases": ["microservice", "微服务架构"], "difficulty": 4},
    1304: {"name": "DDD", "category": "软件工程/方法论", "aliases": ["ddd", "领域驱动设计"], "difficulty": 5},
    1305: {"name": "TDD", "category": "软件工程/方法论", "aliases": ["tdd", "测试驱动开发"], "difficulty": 3},
    1306: {"name": "Clean Code", "category": "软件工程/方法论", "aliases": ["cleancode", "代码整洁"], "difficulty": 2},
    1307: {"name": "设计模式", "category": "软件工程/方法论", "aliases": ["designpattern", "23种设计模式"], "difficulty": 4},
    1308: {"name": "UML", "category": "软件工程/方法论", "aliases": ["uml", "统一建模语言"], "difficulty": 3},
    1309: {"name": "项目管理", "category": "软件工程/方法论", "aliases": ["pm", "projectmanagement"], "difficulty": 3},
    
    # 数据分析/可视化 (1400-1499)
    1400: {"name": "数据分析", "category": "数据分析/可视化", "aliases": ["dataanalysis", "数据分析"], "difficulty": 3},
    1401: {"name": "数据可视化", "category": "数据分析/可视化", "aliases": ["datavisualization", "echarts", "可视化"], "difficulty": 2},
    1402: {"name": "Tableau", "category": "数据分析/可视化", "aliases": ["tableau", "bi工具"], "difficulty": 2},
    1403: {"name": "Power BI", "category": "数据分析/可视化", "aliases": ["powerbi", "bi工具"], "difficulty": 2},
    1404: {"name": "Excel", "category": "数据分析/可视化", "aliases": ["excel", "spreadsheet"], "difficulty": 2},
    1405: {"name": "大数据分析", "category": "数据分析/可视化", "aliases": ["bigdata", "hadoop", "spark"], "difficulty": 4},
    1406: {"name": "数据挖掘", "category": "数据分析/可视化", "aliases": ["datamining", "数据挖掘"], "difficulty": 4},
    1407: {"name": "A/B测试", "category": "数据分析/可视化", "aliases": ["abtest", "abtesting", "实验"], "difficulty": 3},
    
    # UI/UX设计 (1500-1599)
    1500: {"name": "UI设计", "category": "UI/UX设计", "aliases": ["ui", "用户界面设计"], "difficulty": 2},
    1501: {"name": "UX设计", "category": "UI/UX设计", "aliases": ["ux", "用户体验设计"], "difficulty": 2},
    1502: {"name": "Figma", "category": "UI/UX设计", "aliases": ["figma", "设计工具"], "difficulty": 2},
    1503: {"name": "Sketch", "category": "UI/UX设计", "aliases": ["sketch", "mac设计工具"], "difficulty": 2},
    1504: {"name": "Adobe XD", "category": "UI/UX设计", "aliases": ["adobexd", "xd", "设计工具"], "difficulty": 2},
    1505: {"name": "Photoshop", "category": "UI/UX设计", "aliases": ["photoshop", "ps", "图片处理"], "difficulty": 3},
    1506: {"name": "Illustrator", "category": "UI/UX设计", "aliases": ["illustrator", "ai", "矢量图"], "difficulty": 3},
    1507: {"name": "Axure", "category": "UI/UX设计", "aliases": ["axure", "原型设计"], "difficulty": 3},
    
    # 其他/通用技能 (1600+)
    1600: {"name": "算法", "category": "其他/通用技能", "aliases": ["algorithm", "数据结构算法"], "difficulty": 4},
    1601: {"name": "数据结构", "category": "其他/通用技能", "aliases": ["datastructure", "数据结构"], "difficulty": 3},
    1602: {"name": "操作系统", "category": "其他/通用技能", "aliases": ["os", "operatingsystem"], "difficulty": 3},
    1603: {"name": "计算机网络", "category": "其他/通用技能", "aliases": ["computernetwork", "网络"], "difficulty": 3},
    1604: {"name": "数据库原理", "category": "其他/通用技能", "aliases": ["database", "dbms", "数据库原理"], "difficulty": 3},
    1605: {"name": "分布式系统", "category": "其他/通用技能", "aliases": ["distributed", "分布式"], "difficulty": 5},
    1606: {"name": "消息队列", "category": "其他/通用技能", "aliases": ["messagequeue", "mq", "rabbitmq"], "difficulty": 3},
    1607: {"name": "缓存", "category": "其他/通用技能", "aliases": ["cache", "redis", "memcached"], "difficulty": 3},
    1608: {"name": "搜索引擎", "category": "其他/通用技能", "aliases": ["searchengine", "elasticsearch", "solr"], "difficulty": 4},
    1609: {"name": "API设计", "category": "其他/通用技能", "aliases": ["apidesign", "接口设计"], "difficulty": 3},
    1610: {"name": "系统设计", "category": "其他/通用技能", "aliases": ["systemdesign", "架构设计"], "difficulty": 5},
}

# 技能分类统计
SKILL_CATEGORY_STATS = {
    "编程语言": {"count": 20, "difficulty_avg": 2.9},
    "前端技术": {"count": 19, "difficulty_avg": 2.9},
    "后端框架": {"count": 16, "difficulty_avg": 3.6},
    "数据库": {"count": 15, "difficulty_avg": 3.1},
    "大数据": {"count": 12, "difficulty_avg": 4.1},
    "机器学习/AI": {"count": 15, "difficulty_avg": 4.0},
    "DevOps/云计算": {"count": 16, "difficulty_avg": 3.1},
    "云服务": {"count": 11, "difficulty_avg": 3.3},
    "版本控制/协作": {"count": 8, "difficulty_avg": 1.9},
    "移动开发": {"count": 8, "difficulty_avg": 3.5},
    "测试": {"count": 9, "difficulty_avg": 2.4},
    "安全": {"count": 7, "difficulty_avg": 3.6},
    "网络/协议": {"count": 10, "difficulty_avg": 2.8},
    "软件工程/方法论": {"count": 10, "difficulty_avg": 3.2},
    "数据分析/可视化": {"count": 8, "difficulty_avg": 2.9},
    "UI/UX设计": {"count": 8, "difficulty_avg": 2.5},
    "其他/通用技能": {"count": 11, "difficulty_avg": 3.8},
}

def get_all_skills():
    """获取所有技能列表"""
    return STANDARD_SKILLS

def get_skill_by_id(skill_id):
    """根据ID获取技能"""
    return STANDARD_SKILLS.get(skill_id)

def get_skills_by_category(category):
    """根据分类获取技能"""
    return {k: v for k, v in STANDARD_SKILLS.items() if v.get('category') == category}

def get_skill_by_name(name):
    """根据名称获取技能（支持别名）"""
    name_lower = name.lower().strip()
    for skill_id, skill_info in STANDARD_SKILLS.items():
        if skill_info['name'].lower() == name_lower:
            return skill_id, skill_info
        if name_lower in [alias.lower() for alias in skill_info.get('aliases', [])]:
            return skill_id, skill_info
    return None, None

def get_all_skill_names():
    """获取所有技能名称和别名"""
    names = {}
    for skill_id, skill_info in STANDARD_SKILLS.items():
        names[skill_info['name'].lower()] = skill_id
        for alias in skill_info.get('aliases', []):
            names[alias.lower()] = skill_id
    return names

def get_category_keywords():
    """获取分类关键词映射"""
    return {v['category']: [v['name'].lower()] + [a.lower() for a in v.get('aliases', [])]
            for k, v in STANDARD_SKILLS.items()}

# 生成扩展的关键词字典（用于技能识别）
def generate_extended_keywords():
    """生成扩展的关键词字典，用于从文本中识别技能"""
    keywords = {}
    for skill_id, skill_info in STANDARD_SKILLS.items():
        category = skill_info['category']
        if category not in keywords:
            keywords[category] = []
        
        # 添加技能名和所有别名
        all_names = [skill_info['name'].lower()] + [a.lower() for a in skill_info.get('aliases', [])]
        for name in all_names:
            if name not in keywords[category]:
                keywords[category].append(name)
    
    return keywords
