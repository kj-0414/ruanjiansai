import re
from typing import List, Dict, Any

class ResumeSplitter:
    def __init__(self):
        self.section_patterns = {
            'education': r'(教育背景|学历|毕业院校|求学经历)',
            'project': r'(项目经验|项目经历|项目背景)',
            'skills': r'(技能|专业技能|技术能力|掌握技能)',
            'certificates': r'(证书|资格证书|认证)',
            'internship': r'(实习经历|实习)',
            'work': r'(工作经历|工作经验|职业经历)'
        }
    
    def split_resume(self, text: str) -> List[Dict[str, str]]:
        chunks = []
        text = self._clean_text(text)
        
        for section_name, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = match.start()
                end = self._find_section_end(text, start, list(self.section_patterns.keys()))
                section_text = text[start:end].strip()
                
                if len(section_text) > 50:
                    chunks.append({
                        'type': section_name,
                        'content': section_text,
                        'start': start,
                        'end': end
                    })
        
        skill_chunks = self._extract_skill_chunks(text)
        chunks.extend(skill_chunks)
        
        return sorted(chunks, key=lambda x: x['start'])
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：（）《》【】·\-]', '', text)
        return text.strip()
    
    def _find_section_end(self, text: str, start: int, section_names: List[str]) -> int:
        patterns = '|'.join([self.section_patterns[name] for name in section_names])
        matches = list(re.finditer(patterns, text[start+100:], re.IGNORECASE))
        
        if matches:
            return start + 100 + matches[0].start() - 30
        return len(text)
    
    def _extract_skill_chunks(self, text: str) -> List[Dict[str, str]]:
        skill_pattern = r'[A-Za-z][A-Za-z0-9._-]*'
        matches = re.finditer(skill_pattern, text)
        
        chunks = []
        for match in matches:
            skill = match.group()
            if 2 <= len(skill) <= 50:
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                context = text[start:end]
                
                if len(context) >= 50:
                    chunks.append({
                        'type': 'skill_phrase',
                        'content': context,
                        'start': start,
                        'end': end
                    })
        
        return chunks

class JDSplitter:
    def __init__(self):
        self.responsibility_pattern = r'(岗位职责|工作内容|主要职责|工作职责)'
        self.requirement_pattern = r'(任职要求|岗位要求|职位要求|招聘要求)'
        self.hard_requirement_pattern = r'(学历|本科|硕士|博士|专业|年限|经验)'
        self.soft_requirement_pattern = r'(技能|熟悉|掌握|了解|沟通|团队|能力)'
    
    def split_jd(self, text: str) -> List[Dict[str, str]]:
        chunks = []
        text = self._remove_redundant(text)
        
        responsibility_match = re.search(self.responsibility_pattern, text, re.IGNORECASE)
        if responsibility_match:
            start = responsibility_match.start()
            requirement_match = re.search(self.requirement_pattern, text[start:], re.IGNORECASE)
            
            if requirement_match:
                end = start + requirement_match.start()
            else:
                end = len(text)
            
            chunks.append({
                'type': 'responsibility',
                'content': text[start:end].strip()
            })
        
        requirement_match = re.search(self.requirement_pattern, text, re.IGNORECASE)
        if requirement_match:
            start = requirement_match.start()
            requirement_text = text[start:].strip()
            
            hard_parts = []
            soft_parts = []
            
            lines = requirement_text.split('\n')
            for line in lines:
                if re.search(self.hard_requirement_pattern, line, re.IGNORECASE):
                    hard_parts.append(line)
                elif re.search(self.soft_requirement_pattern, line, re.IGNORECASE):
                    soft_parts.append(line)
            
            if hard_parts:
                chunks.append({
                    'type': 'hard_requirement',
                    'content': '\n'.join(hard_parts)
                })
            
            if soft_parts:
                chunks.append({
                    'type': 'soft_requirement',
                    'content': '\n'.join(soft_parts)
                })
        
        return chunks
    
    def _remove_redundant(self, text: str) -> str:
        redundant_patterns = [
            r'公司介绍.*?(职位描述|岗位职责)',
            r'【.*招聘.*】',
            r'投递邮箱.*',
            r'联系人.*',
            r'公司地址.*'
        ]
        
        for pattern in redundant_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL)
        
        return text.strip()
