"""
语义匹配器 - 使用Sentence-BERT实现（带降级方案）
提供高精度的技能语义相似度匹配
"""

from typing import List, Tuple, Dict, Optional, Set


class SemanticMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化语义匹配器
        
        Args:
            model_name: Sentence-BERT模型名称，默认为all-MiniLM-L6-v2
        """
        self.model = None
        self.use_embedding = False
        self.model_initialized = False
        self.model_name = model_name
        self.default_threshold = 0.7
        self.certificate_threshold = 0.8
        
        self.skill_synonyms = {
            "vue.js": ["vue", "vue3", "vue2", "vue.js"],
            "react": ["react", "react.js", "reactjs"],
            "javascript": ["javascript", "js", "ecmascript"],
            "typescript": ["typescript", "ts"],
            "python": ["python", "py"],
            "java": ["java", "jdk", "jvm"],
            "node.js": ["node.js", "node", "nodejs"],
            "mysql": ["mysql", "sql"],
            "redis": ["redis", "cache"],
            "mongodb": ["mongodb", "nosql", "mongo"],
            "docker": ["docker", "container"],
            "kubernetes": ["kubernetes", "k8s"],
            "git": ["git", "version control"],
            "webpack": ["webpack", "bundler"],
            "npm": ["npm", "node package manager"],
            "yarn": ["yarn", "package manager"],
            "css": ["css", "css3", "stylesheet"],
            "html": ["html", "html5", "markup"],
            "sass": ["sass", "scss", "css preprocessor"],
            "less": ["less", "css preprocessor"],
            "bootstrap": ["bootstrap", "css framework"],
            "tailwind": ["tailwind", "tailwindcss", "utility css"],
            "jquery": ["jquery", "js library"],
            "axios": ["axios", "http client"],
            "webpack": ["webpack", "module bundler"],
            "vite": ["vite", "build tool"],
            "django": ["django", "python framework"],
            "flask": ["flask", "python microframework"],
            "spring": ["spring", "spring boot", "java framework"],
            "hibernate": ["hibernate", "orm"],
            "mybatis": ["mybatis", "data access"],
            "postgresql": ["postgresql", "postgres", "pg"],
            "oracle": ["oracle", "oracle database"],
            "sqlserver": ["sqlserver", "mssql", "microsoft sql"],
            "elasticsearch": ["elasticsearch", "es", "search engine"],
            "rabbitmq": ["rabbitmq", "message queue"],
            "kafka": ["kafka", "streaming"],
            "nginx": ["nginx", "web server", "reverse proxy"],
            "apache": ["apache", "http server"],
            "linux": ["linux", "unix", "operating system"],
            "windows": ["windows", "os"],
            "aws": ["aws", "amazon web services", "cloud"],
            "azure": ["azure", "microsoft cloud"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "terraform": ["terraform", "infrastructure as code", "iac"],
            "jenkins": ["jenkins", "ci/cd", "continuous integration"],
            "gitlab": ["gitlab", "git hosting", "devops"],
            "github": ["github", "git hosting"],
            "docker-compose": ["docker-compose", "container orchestration"]
        }
    
    def _try_init_model(self):
        """延迟初始化Sentence-BERT模型"""
        if self.model_initialized:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.use_embedding = True
            print(f"[SemanticMatcher] Sentence-BERT model loaded: {self.model_name}")
        except Exception as e:
            print(f"[SemanticMatcher] Falling back to rule-based matching: {e}")
            self.use_embedding = False
        finally:
            self.model_initialized = True
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算语义相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        text1_lower = text1.lower().strip()
        text2_lower = text2.lower().strip()
        
        if text1_lower == text2_lower:
            return 1.0
        
        for skill, synonyms in self.skill_synonyms.items():
            if text1_lower in synonyms and text2_lower in synonyms:
                return 0.9
        
        text1_clean = self._clean_version(text1_lower)
        text2_clean = self._clean_version(text2_lower)
        
        if text1_clean in text2_clean or text2_clean in text1_clean:
            return 0.85
        
        if not self.model_initialized:
            self._try_init_model()
        
        if self.use_embedding and self.model is not None:
            try:
                from sentence_transformers import util
                embeddings = self.model.encode([text1_clean, text2_clean])
                return util.cos_sim(embeddings[0], embeddings[1]).item()
            except:
                pass
        
        return self._calculate_jaccard_similarity(text1_clean, text2_clean)
    
    def _clean_version(self, text: str) -> str:
        """移除版本号，保留核心名称"""
        import re
        return re.sub(r'\d+(\.\d+)*', '', text).strip()
    
    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """计算Jaccard相似度（降级方案）"""
        keywords1 = set(text1.split())
        keywords2 = set(text2.split())
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        jaccard_score = len(intersection) / len(union)
        
        tech_keywords = {"vue", "react", "java", "python", "sql", "node", "js", "css", "html"}
        common_tech = keywords1 & keywords2 & tech_keywords
        
        if common_tech:
            jaccard_score = min(jaccard_score + 0.2, 1.0)
        
        return jaccard_score
    
    def match_skill(self, job_skill: str, seeker_skills: list, threshold: float = None) -> tuple:
        """
        在求职者技能列表中查找最匹配的技能
        
        Args:
            job_skill: 岗位要求的技能
            seeker_skills: 求职者的技能列表
            threshold: 匹配阈值，默认为default_threshold
        
        Returns:
            (匹配的技能, 相似度分数)，未匹配返回(None, 0)
        """
        if not seeker_skills:
            return None, 0.0
        
        threshold = threshold if threshold is not None else self.default_threshold
        
        if not self.model_initialized:
            self._try_init_model()
        
        if self.use_embedding and self.model is not None:
            try:
                from sentence_transformers import util
                embeddings = self.model.encode([job_skill] + seeker_skills)
                similarities = util.cos_sim(embeddings[0], embeddings[1:])
                
                best_idx = similarities.argmax().item()
                best_score = similarities[0][best_idx].item()
                
                if best_score >= threshold:
                    return seeker_skills[best_idx], best_score
                
                return None, 0.0
            except:
                pass
        
        best_match = None
        best_score = 0.0
        
        for seeker_skill in seeker_skills:
            score = self.calculate_similarity(job_skill, seeker_skill)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = seeker_skill
        
        return best_match, best_score
    
    def batch_match_skills(self, job_skills: List[str], seeker_skills: List[str]) -> Dict[str, Tuple[str, float]]:
        """
        批量匹配技能
        
        Args:
            job_skills: 岗位要求的技能列表
            seeker_skills: 求职者的技能列表
        
        Returns:
            匹配结果字典 {job_skill: (matched_skill, score)}
        """
        if not job_skills or not seeker_skills:
            return {}
        
        if self.use_embedding and self.model is not None:
            try:
                from sentence_transformers import util
                job_embeddings = self.model.encode(job_skills)
                seeker_embeddings = self.model.encode(seeker_skills)
                
                similarities = util.cos_sim(job_embeddings, seeker_embeddings)
                
                results = {}
                for i, job_skill in enumerate(job_skills):
                    row = similarities[i]
                    best_idx = row.argmax().item()
                    best_score = row[best_idx].item()
                    
                    if best_score >= self.default_threshold:
                        results[job_skill] = (seeker_skills[best_idx], best_score)
                    else:
                        results[job_skill] = (None, 0.0)
                
                return results
            except:
                pass
        
        results = {}
        for job_skill in job_skills:
            matched, score = self.match_skill(job_skill, seeker_skills)
            results[job_skill] = (matched, score)
        
        return results
    
    def match_project(self, job_project: dict, seeker_projects: list) -> tuple:
        """
        匹配项目经历（考虑技术栈和领域）
        
        Args:
            job_project: 岗位要求的项目
            seeker_projects: 求职者的项目列表
        
        Returns:
            (匹配的项目, 综合相似度分数)，未匹配返回(None, 0)
        """
        if not seeker_projects:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        job_name = job_project.get("name", "")
        job_tech_stack = self._extract_tech_stack(job_project)
        job_domain = job_project.get("领域", "") or job_project.get("domain", "")
        
        for seeker_project in seeker_projects:
            seeker_name = seeker_project.get("name", "")
            seeker_tech_stack = self._extract_tech_stack(seeker_project)
            seeker_domain = seeker_project.get("领域", "") or seeker_project.get("domain", "")
            
            name_score = self.calculate_similarity(job_name, seeker_name)
            tech_score = self._calculate_tech_match(job_tech_stack, seeker_tech_stack)
            domain_score = self.calculate_similarity(job_domain, seeker_domain) if job_domain else 0.5
            
            overall_score = tech_score * 0.7 + domain_score * 0.2 + name_score * 0.1
            
            if overall_score > best_score and overall_score >= self.default_threshold:
                best_score = overall_score
                best_match = seeker_project
        
        return best_match, best_score
    
    def _extract_tech_stack(self, project: dict) -> list:
        """从项目中提取技术栈"""
        tech_stack = []
        
        if "children" in project:
            for child in project["children"]:
                if child.get("name") == "技术栈":
                    value = child.get("value", [])
                    if isinstance(value, list):
                        tech_stack.extend(value)
                    elif isinstance(value, str):
                        tech_stack.extend([s.strip() for s in value.split(",") if s.strip()])
        
        if not tech_stack and "技术栈" in project:
            value = project["技术栈"]
            if isinstance(value, list):
                tech_stack.extend(value)
            elif isinstance(value, str):
                tech_stack.extend([s.strip() for s in value.split(",") if s.strip()])
        
        if not tech_stack and "name" in project:
            name = project["name"]
            for keyword in ["vue", "react", "java", "python", "node", "sql", "mysql", "redis"]:
                if keyword in name.lower():
                    tech_stack.append(keyword)
        
        return tech_stack
    
    def _calculate_tech_match(self, job_tech: list, seeker_tech: list) -> float:
        """计算技术栈匹配度"""
        if not job_tech:
            return 1.0
        
        if not seeker_tech:
            return 0.0
        
        matched_count = 0
        for job_skill in job_tech:
            _, score = self.match_skill(job_skill, seeker_tech)
            if score >= self.default_threshold:
                matched_count += 1
        
        return matched_count / len(job_tech)
    
    def match_certificate(self, job_cert: str, seeker_certs: list) -> tuple:
        """
        匹配证书（使用更高的阈值）
        
        Args:
            job_cert: 岗位要求的证书
            seeker_certs: 求职者的证书列表
        
        Returns:
            (匹配的证书, 相似度分数)，未匹配返回(None, 0)
        """
        return self.match_skill(job_cert, seeker_certs, threshold=self.certificate_threshold)
    
    def calculate_certificate_bonus(self, seeker_certs: list) -> int:
        """
        计算证书加分
        
        Args:
            seeker_certs: 求职者的证书列表
        
        Returns:
            加分值（最多20分）
        """
        bonus_points = 0
        valuable_certs = [
            "PMP", "CFA", "CPA", "FRM", "AWS", "Azure", "GCP",
            "软件设计师", "系统架构师", "网络工程师", "信息安全",
            "教师资格证", "执业医师", "护士资格证", "律师资格证",
            "注册会计师", "注册工程师", "建造师", "安全工程师"
        ]
        
        for cert in seeker_certs:
            cert_lower = cert.lower()
            for valuable_cert in valuable_certs:
                if valuable_cert.lower() in cert_lower:
                    bonus_points += 5
                    break
        
        return min(bonus_points, 20)


semantic_matcher = SemanticMatcher()