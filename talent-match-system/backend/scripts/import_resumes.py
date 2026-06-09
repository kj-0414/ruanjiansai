import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from models import get_db, Resume, User, Base, engine
import json

def create_sample_resumes():
    db = next(get_db())
    
    job_seeker_user = db.query(User).filter(User.roles.like('%job_seeker%')).first()
    if not job_seeker_user:
        print("未找到求职者用户，请先创建用户")
        return
    
    user_id = job_seeker_user.id
    
    resumes = [
        {
            "resume_name": "个人简历-张伟",
            "filename": "zhangwei_resume.pdf",
            "filepath": "/uploads/resumes/zhangwei_resume.pdf",
            "user_id": user_id,
            "name": "张伟",
            "phone": "13800138001",
            "email": "zhangwei@example.com",
            "desired_position": "Java后端开发工程师",
            "address": "上海市浦东新区",
            "education": "本科",
            "school": "XX大学",
            "major": "计算机科学与技术",
            "degree": "学士",
            "experience": "3年工作经验",
            "work_years": 3,
            "desired_salary": "15k-25k",
            "self_evaluation": "本人性格开朗、稳重、有活力，待人热情、真诚。工作认真负责，积极主动，能吃苦耐劳。有较强的组织能力、实际动手能力和团队协作精神，能迅速的适应各种环境，并融合其中。",
            "skills": json.dumps(["Java", "Spring Boot", "MySQL", "Redis", "Spring Cloud", "Linux", "Docker", "Vue.js"]),
            "skills_detail": json.dumps([
                {"name": "Java", "level": "精通", "experience": "3年"},
                {"name": "Spring Boot", "level": "精通", "experience": "2年"},
                {"name": "MySQL", "level": "熟练", "experience": "3年"},
                {"name": "Redis", "level": "熟练", "experience": "2年"},
                {"name": "Spring Cloud", "level": "熟练", "experience": "1年"},
                {"name": "Linux", "level": "熟练", "experience": "3年"},
                {"name": "Docker", "level": "了解", "experience": "1年"},
                {"name": "Vue.js", "level": "了解", "experience": "6个月"}
            ]),
            "work_experience": json.dumps([
                {
                    "company": "XX科技有限公司",
                    "position": "后端开发工程师",
                    "start_date": "2021-07",
                    "end_date": "至今",
                    "description": "负责核心业务系统开发与维护，参与微服务架构改造"
                },
                {
                    "company": "XX互联网公司",
                    "position": "Java开发实习生",
                    "start_date": "2020-07",
                    "end_date": "2020-09",
                    "description": "参与电商平台后端开发，学习企业级开发规范"
                }
            ]),
            "projects": json.dumps([
                {
                    "name": "企业级微服务平台",
                    "role": "核心开发",
                    "start_date": "2022-01",
                    "end_date": "2023-06",
                    "description": "负责用户服务、订单服务的设计与开发",
                    "technologies": "Java/Spring Boot/Spring Cloud/MySQL/Redis"
                },
                {
                    "name": "智能风控系统",
                    "role": "开发人员",
                    "start_date": "2021-09",
                    "end_date": "2021-12",
                    "description": "参与风控规则引擎的开发",
                    "technologies": "Java/Redis/Kafka"
                }
            ]),
            "certificates": json.dumps([
                {"name": "软件设计师", "issuer": "国家人力资源和社会保障部", "date": "2022-11", "level": "中级"},
                {"name": "计算机二级（Java）", "issuer": "教育部考试中心", "date": "2020-03", "level": "合格"},
                {"name": "大学英语四级", "issuer": "教育部考试中心", "date": "2018-12", "level": "520分"}
            ]),
            "honors": json.dumps([
                {"name": "校级一等奖学金", "issuer": "XX大学", "date": "2020-09"},
                {"name": "校级一等奖学金", "issuer": "XX大学", "date": "2021-09"},
                {"name": "ACM程序设计竞赛省级三等奖", "issuer": "XX省教育厅", "date": "2020-11"},
                {"name": "优秀毕业生", "issuer": "XX大学", "date": "2021-06"}
            ])
        },
        {
            "resume_name": "个人简历-李娜",
            "filename": "lina_resume.pdf",
            "filepath": "/uploads/resumes/lina_resume.pdf",
            "user_id": user_id,
            "name": "李娜",
            "phone": "13900139002",
            "email": "lina@example.com",
            "desired_position": "前端开发工程师",
            "address": "北京市朝阳区",
            "education": "本科",
            "school": "YY大学",
            "major": "软件工程",
            "degree": "学士",
            "experience": "2年工作经验",
            "work_years": 2,
            "desired_salary": "12k-20k",
            "self_evaluation": "热爱前端开发，对新技术有强烈的好奇心。具备良好的沟通能力和团队协作精神，能够快速融入团队。",
            "skills": json.dumps(["Vue.js", "React", "TypeScript", "JavaScript", "CSS3", "HTML5", "Webpack", "Node.js"]),
            "skills_detail": json.dumps([
                {"name": "Vue.js", "level": "精通", "experience": "2年"},
                {"name": "React", "level": "熟练", "experience": "1年"},
                {"name": "TypeScript", "level": "精通", "experience": "2年"},
                {"name": "JavaScript", "level": "精通", "experience": "3年"},
                {"name": "CSS3", "level": "熟练", "experience": "2年"},
                {"name": "HTML5", "level": "精通", "experience": "3年"},
                {"name": "Webpack", "level": "熟练", "experience": "1年"},
                {"name": "Node.js", "level": "了解", "experience": "6个月"}
            ]),
            "work_experience": json.dumps([
                {
                    "company": "ZZ科技有限公司",
                    "position": "前端开发工程师",
                    "start_date": "2022-03",
                    "end_date": "至今",
                    "description": "负责公司核心产品的前端开发，参与多个大型项目"
                }
            ]),
            "projects": json.dumps([
                {
                    "name": "电商平台前端重构",
                    "role": "前端负责人",
                    "start_date": "2022-06",
                    "end_date": "2023-03",
                    "description": "带领团队完成电商平台的Vue3+TypeScript重构",
                    "technologies": "Vue3/TypeScript/Vite/TailwindCSS"
                },
                {
                    "name": "数据可视化平台",
                    "role": "开发人员",
                    "start_date": "2022-09",
                    "end_date": "2022-12",
                    "description": "参与数据可视化平台的开发",
                    "technologies": "React/ECharts/TypeScript"
                }
            ]),
            "certificates": json.dumps([
                {"name": "Web前端开发工程师", "issuer": "工信部", "date": "2022-06", "level": "中级"}
            ])
        },
        {
            "resume_name": "个人简历-王磊",
            "filename": "wanglei_resume.pdf",
            "filepath": "/uploads/resumes/wanglei_resume.pdf",
            "user_id": user_id,
            "name": "王磊",
            "phone": "13700137003",
            "email": "wanglei@example.com",
            "desired_position": "全栈开发工程师",
            "address": "深圳市南山区",
            "education": "硕士",
            "school": "ZZ大学",
            "major": "计算机应用技术",
            "degree": "硕士",
            "experience": "5年工作经验",
            "work_years": 5,
            "desired_salary": "25k-35k",
            "self_evaluation": "5年全栈开发经验，熟悉前后端技术栈。具备良好的架构设计能力和问题解决能力。",
            "skills": json.dumps(["Java", "Python", "Vue.js", "React", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes"]),
            "skills_detail": json.dumps([
                {"name": "Java", "level": "精通", "experience": "5年"},
                {"name": "Python", "level": "熟练", "experience": "3年"},
                {"name": "Vue.js", "level": "精通", "experience": "4年"},
                {"name": "React", "level": "熟练", "experience": "2年"},
                {"name": "MySQL", "level": "精通", "experience": "5年"},
                {"name": "MongoDB", "level": "熟练", "experience": "3年"},
                {"name": "Redis", "level": "熟练", "experience": "4年"},
                {"name": "Docker", "level": "熟练", "experience": "2年"},
                {"name": "Kubernetes", "level": "了解", "experience": "1年"}
            ]),
            "work_experience": json.dumps([
                {
                    "company": "AA科技有限公司",
                    "position": "全栈开发工程师",
                    "start_date": "2021-03",
                    "end_date": "至今",
                    "description": "负责公司核心系统的全栈开发，参与技术架构设计"
                },
                {
                    "company": "BB软件公司",
                    "position": "后端开发工程师",
                    "start_date": "2019-07",
                    "end_date": "2021-02",
                    "description": "负责企业级应用的后端开发"
                }
            ]),
            "projects": json.dumps([
                {
                    "name": "企业级OA系统",
                    "role": "技术负责人",
                    "start_date": "2021-06",
                    "end_date": "2022-12",
                    "description": "负责系统架构设计和核心功能开发",
                    "technologies": "Java/Spring Boot/Vue.js/MySQL/Redis"
                },
                {
                    "name": "在线教育平台",
                    "role": "全栈开发",
                    "start_date": "2020-03",
                    "end_date": "2021-03",
                    "description": "负责前端和后端的开发工作",
                    "technologies": "Python/Django/Vue.js/PostgreSQL"
                }
            ]),
            "certificates": json.dumps([
                {"name": "系统架构设计师", "issuer": "国家人力资源和社会保障部", "date": "2023-05", "level": "高级"},
                {"name": "AWS解决方案架构师", "issuer": "Amazon", "date": "2022-08", "level": "Associate"}
            ]),
            "honors": json.dumps([
                {"name": "优秀员工", "issuer": "AA科技有限公司", "date": "2022-12"},
                {"name": "技术创新奖", "issuer": "AA科技有限公司", "date": "2023-06"}
            ])
        }
    ]
    
    for resume_data in resumes:
        existing_resume = db.query(Resume).filter(Resume.resume_name == resume_data["resume_name"]).first()
        if existing_resume:
            print(f"简历 {resume_data['resume_name']} 已存在，跳过")
            continue
        
        resume = Resume(
            resume_name=resume_data["resume_name"],
            filename=resume_data["filename"],
            filepath=resume_data["filepath"],
            user_id=resume_data["user_id"],
            name=resume_data["name"],
            phone=resume_data["phone"],
            email=resume_data["email"],
            desired_position=resume_data["desired_position"],
            address=resume_data["