import os
import re
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_path):
    """
    从PDF文件中提取文本
    :param file_path: PDF文件路径
    :return: 提取的文本内容
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF解析错误: {e}")
        return ""

def extract_text_from_docx(file_path):
    """
    从DOCX文件中提取文本
    :param file_path: DOCX文件路径
    :return: 提取的文本内容
    """
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"DOCX解析错误: {e}")
        return ""

def extract_name(text):
    """
    从文本中提取姓名
    :param text: 简历文本内容
    :return: 姓名
    """
    # 常见姓名匹配模式
    name_patterns = [
        r'姓名[：:]\s*([\u4e00-\u9fa5]{2,4})',
        r'^[\u4e00-\u9fa5]{2,4}(?=[\s\n])',
        r'Name[：:]\s*([\u4e00-\u9fa5]{2,4})',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    
    return "未知"

def extract_phone(text):
    """
    从文本中提取手机号
    :param text: 简历文本内容
    :return: 手机号
    """
    # 手机号正则表达式
    phone_pattern = r'1[3-9]\d{9}'
    match = re.search(phone_pattern, text)
    if match:
        return match.group(0)
    return ""

def extract_email(text):
    """
    从文本中提取邮箱
    :param text: 简历文本内容
    :return: 邮箱
    """
    # 邮箱正则表达式
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return ""

def extract_education(text):
    """
    从文本中提取学历信息
    :param text: 简历文本内容
    :return: 学历
    """
    # 学历关键词（只保留到大专）
    education_keywords = ['博士', '硕士', '本科', '大专']
    
    for keyword in education_keywords:
        if keyword in text:
            return keyword
    
    # 尝试匹配"学历：xxx"模式
    edu_pattern = r'学历[：:]\s*([\u4e00-\u9fa5]+)'
    match = re.search(edu_pattern, text)
    if match:
        return match.group(1)
    
    return "未知"

def extract_experience(text):
    """
    从文本中提取工作经验
    :param text: 简历文本内容
    :return: 工作经验描述
    """
    # 尝试匹配"经验：xxx"或"工作经验"模式
    exp_patterns = [
        r'工作经验[：:]\s*(.+?)(?:\n|$)',
        r'经验[：:]\s*(\d+年?)',
        r'(\d+)\s*年\s*经验',
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return "未知"

def extract_skills(text):
    """
    从文本中提取技能
    :param text: 简历文本内容
    :return: 技能列表
    """
    # 常见技能关键词
    skill_keywords = [
        'Python', 'Java', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'PHP', 'Ruby',
        'Swift', 'Kotlin', 'Objective-C', 'Scala', 'Perl', 'Lua', 'R', 'MATLAB',
        'HTML', 'CSS', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring',
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server',
        'Linux', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', '阿里云', '腾讯云',
        'Git', 'Jenkins', 'CI/CD', 'Nginx', 'Apache', 'Tomcat',
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
        'NLP', 'Computer Vision', 'Data Analysis', 'Big Data', 'Hadoop', 'Spark',
        'Android', 'iOS', 'Flutter', 'React Native', 'WeChat Mini Program',
        'Photoshop', 'Illustrator', 'Figma', 'Sketch', 'Axure',
        '项目管理', '团队协作', '沟通能力', '问题解决'
    ]
    
    found_skills = []
    for skill in skill_keywords:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    
    # 如果没有找到技能，尝试从"技能"关键词后提取
    if not found_skills:
        skill_pattern = r'技能[：:]\s*(.+?)(?:\n|$)'
        match = re.search(skill_pattern, text)
        if match:
            skills_text = match.group(1)
            # 按逗号、顿号或空格分割
            skills_list = re.split(r'[,，、\s]+', skills_text)
            found_skills = [s.strip() for s in skills_list if s.strip()]
    
    return found_skills if found_skills else ["未识别到技能"]

def parse_resume(file_path):
    """
    解析简历文件，提取关键信息
    :param file_path: 简历文件路径
    :return: 解析后的简历信息字典
    """
    # 根据文件类型提取文本
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return {
            "name": "未知",
            "phone": "",
            "email": "",
            "education": "未知",
            "experience": "未知",
            "skills": ["未识别到技能"]
        }
    
    # 如果文本提取失败，返回默认值
    if not text.strip():
        return {
            "name": "未知",
            "phone": "",
            "email": "",
            "education": "未知",
            "experience": "未知",
            "skills": ["未识别到技能"]
        }
    
    # 提取各项信息
    resume_data = {
        "name": extract_name(text),
        "phone": extract_phone(text),
        "email": extract_email(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "skills": extract_skills(text)
    }
    
    return resume_data