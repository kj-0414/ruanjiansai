﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿<template>
  <div class="resume-page">
    <div class="container">
      <div class="page-header">
        <div class="header-top">
          <el-button @click="goBack" class="back-btn">
            <el-icon><ArrowLeft /></el-icon> 返回列表
          </el-button>
        </div>
        <h1 class="page-title">{{ isViewMode ? '查看简历' : (currentResumeId ? '编辑简历' : '新建简历') }}</h1>
        <p class="page-subtitle">{{ isViewMode ? '查看简历详情' : (currentResumeId ? '修改简历信息' : '上传简历，AI智能解析，轻松生成结构化简历') }}</p>
      </div>

      <div class="upload-section" v-if="!currentResumeId && !isViewMode">
        <div class="upload-card">
          <div class="upload-icon">
            <el-icon :size="48"><Upload /></el-icon>
          </div>
          <h3 class="upload-title">上传简历文件</h3>
          <p class="upload-desc">支持 PDF、Word、图片格式，AI自动解析</p>
          <el-upload
            class="upload-component"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
            :file-list="uploadedFiles"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖放文件到此处，或<em>点击选择</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">文件大小不超过 10MB</div>
            </template>
          </el-upload>

          <div v-if="uploadedFiles.length > 0" class="upload-actions">
            <el-button type="primary" size="large" :loading="isAnalyzing" @click="analyzeFile">
              <el-icon><MagicStick /></el-icon>
              {{ isAnalyzing ? "AI解析中..." : "开始AI解析" }}
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="resumeData" class="form-section">
        <div class="progress-card" v-if="!isViewMode">
          <div class="progress-header">
            <span class="progress-label">填写进度</span>
            <span class="progress-value">{{ completionRate }}%</span>
          </div>
          <el-progress :percentage="completionRate" :color="progressColor" :stroke-width="8" />
        </div>

        <el-form ref="formRef" :model="resumeData" label-position="top" class="resume-form">
          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">👤</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">个人信息</h3>
                <span class="section-badge required" v-if="!isViewMode">必填</span>
              </div>
            </div>
            <div class="section-content">
              <div class="info-group">
                <h4 class="group-title">基本信息</h4>
                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-form-item label="姓名">
                      <el-input v-model="resumeData.name" placeholder="请输入姓名" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-form-item label="年龄">
                      <el-input v-model="resumeData.age" placeholder="请输入年龄" size="large" :disabled="isViewMode" type="number" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-form-item label="电话">
                      <el-input v-model="resumeData.phone" placeholder="请输入手机号" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="8">
                    <el-form-item label="邮箱">
                      <el-input v-model="resumeData.email" placeholder="请输入邮箱" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>

              <div class="info-group">
                <h4 class="group-title">教育经历</h4>
                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="学校">
                      <el-input v-model="resumeData.school" placeholder="请输入学校" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="专业">
                      <el-input v-model="resumeData.major" placeholder="请输入专业" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="学历">
                      <el-select v-model="resumeData.degree" placeholder="请选择学历" size="large" style="width: 100%" :disabled="isViewMode">
                        <el-option label="高中" value="高中" />
                        <el-option label="大专" value="大专" />
                        <el-option label="本科" value="本科" />
                        <el-option label="硕士" value="硕士" />
                        <el-option label="博士" value="博士" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-form-item label="毕业时间">
                      <el-date-picker v-model="resumeData.graduation_date" type="month" placeholder="选择毕业时间" size="large" style="width: 100%" :disabled="isViewMode" format="YYYY-MM" value-format="YYYY-MM" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>

              <div class="info-group">
                <h4 class="group-title">个人简介</h4>
                <el-input v-model="resumeData.self_evaluation" type="textarea" :rows="4" placeholder="简要介绍一下自己..." size="large" :disabled="isViewMode" />
              </div>
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">💡</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">专业技能</h3>
                <span class="section-badge required" v-if="!isViewMode">必填</span>
              </div>
            </div>
            <div class="section-content">
              <div class="skills-wrapper">
                <el-tag
                  v-for="(skill, index) in resumeData.skills"
                  :key="index"
                  :closable="!isViewMode"
                  @close="removeSkill(index)"
                  class="skill-tag"
                >{{ skill }}</el-tag>
                <el-button v-if="!isViewMode" text @click="addSkillInput" class="add-skill-btn">
                  <el-icon><Plus /></el-icon> 添加技能
                </el-button>
              </div>
              <el-input v-if="showSkillInput && !isViewMode" v-model="newSkill" @keyup.enter="saveSkill" @blur="cancelSkill" placeholder="输入技能后按回车" class="skill-input" />
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">💼</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">实践经历</h3>
                <span class="section-badge optional" v-if="!isViewMode">选填</span>
              </div>
              <el-button v-if="!isViewMode" text @click="addExperience" class="add-btn">
                <el-icon><Plus /></el-icon> 添加经历
              </el-button>
            </div>
            <div class="section-content">
              <div v-if="resumeData.experiences.length === 0" class="empty-state">暂无经历，点击上方添加工作、实习或项目</div>
              <div v-for="(exp, index) in resumeData.experiences" :key="index" class="experience-card">
                <div class="exp-header">
                  <el-select v-model="exp.type" placeholder="类型" size="large" style="width: 120px" :disabled="isViewMode">
                    <el-option label="全职工作" value="work" />
                    <el-option label="实习" value="internship" />
                    <el-option label="项目" value="project" />
                  </el-select>
                  <el-button v-if="!isViewMode" link type="danger" @click="removeExperience(index)">删除</el-button>
                </div>
                <el-row :gutter="15">
                  <el-col :xs="24" :md="8">
                    <el-form-item :label="exp.type === 'project' ? '项目名称' : '公司名称'">
                      <el-input v-model="exp.company" :placeholder="exp.type === 'project' ? '请输入项目名称' : '请输入公司名称'" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="8">
                    <el-form-item :label="exp.type === 'project' ? '角色' : '职位'">
                      <el-input v-model="exp.position" :placeholder="exp.type === 'project' ? '请输入角色' : '请输入职位'" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="8">
                    <el-form-item label="时间">
                      <el-input v-model="exp.period" placeholder="如：2021-06 至 2023-03" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24">
                    <el-form-item label="描述">
                      <el-input v-model="exp.description" type="textarea" :rows="3" placeholder="请描述工作内容" size="large" :disabled="isViewMode" @blur="() => extractTechStack(exp)" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24">
                    <el-form-item label="技术栈">
                      <el-input v-model="exp.tech_stack" placeholder="用逗号分隔" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">🏆</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">获奖荣誉</h3>
                <span class="section-badge optional" v-if="!isViewMode">选填</span>
              </div>
              <el-button v-if="!isViewMode" text @click="addHonor" class="add-btn">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            <div class="section-content">
              <div v-if="resumeData.honors.length === 0" class="empty-state">暂无荣誉，点击上方添加</div>
              <div v-for="(honor, index) in resumeData.honors" :key="index" class="honor-item">
                <div class="honor-header">
                  <span class="honor-index">{{ index + 1 }}</span>
                  <el-button v-if="!isViewMode" link type="danger" @click="removeHonor(index)">删除</el-button>
                </div>
                <el-row :gutter="15">
                  <el-col :xs="24" :md="12">
                    <el-form-item label="荣誉名称">
                      <el-input v-model="honor.name" placeholder="如：校级一等奖学金" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="6">
                    <el-form-item label="颁发方">
                      <el-input v-model="honor.issuer" placeholder="如：清华大学" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="6">
                    <el-form-item label="时间">
                      <el-input v-model="honor.date" placeholder="如：2023-09" size="large" :disabled="isViewMode" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>

          <div class="form-footer" v-if="!isViewMode">
            <el-button size="large" @click="saveDraft">
              <el-icon><Document /></el-icon> 保存草稿
            </el-button>
            <el-button type="primary" size="large" :loading="isSaving" @click="saveResume">
              <el-icon><Check /></el-icon> {{ isSaving ? "保存中..." : "生成并保存简历" }}
            </el-button>
          </div>
          
          <div class="form-footer" v-if="isViewMode">
            <el-button type="primary" size="large" @click="goBack">
              <el-icon><ArrowLeft /></el-icon> 返回列表
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { ElMessage } from "element-plus"
import { Upload, UploadFilled, MagicStick, Plus, Document, Check, ArrowLeft } from "@element-plus/icons-vue"
import service from "../services/request"

const router = useRouter()
const route = useRoute()
const uploadedFiles = ref([])
const isAnalyzing = ref(false)
const isSaving = ref(false)
const resumeData = ref(null)
const showSkillInput = ref(false)
const newSkill = ref("")
const isViewMode = ref(false)
const currentResumeId = ref(null)

const createEmptyResume = () => ({
  name: "",
  age: "",
  phone: "",
  email: "",
  school: "",
  major: "",
  degree: "",
  graduation_date: "",
  skills: [],
  honors: [],
  experiences: [],
  self_evaluation: ""
})

const techKeywords = [
  "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Swift", "Kotlin",
  "React", "Vue", "Vue3", "Angular", "Next.js", "Nuxt.js", "Svelte",
  "Spring", "Spring Boot", "Spring MVC", "Django", "Flask", "FastAPI", "Express", "Nest.js",
  "MySQL", "PostgreSQL", "Oracle", "SQL Server", "MongoDB", "Redis", "Elasticsearch", "达梦数据库",
  "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "K8s",
  "HTML", "CSS", "SCSS", "Less", "Tailwind", "Element Plus", "Element UI", "Ant Design",
  "Node.js", "npm", "yarn", "pnpm", "Vite", "Webpack",
  "Linux", "Windows", "Ubuntu", "CentOS",
  "REST API", "GraphQL", "WebSocket", "HTTP", "HTTPS", "TCP/IP",
  "敏捷开发", "Scrum", "Jira", "Confluence",
  "测试", "单元测试", "集成测试", "自动化测试", "Jenkins",
  "大数据", "AI", "机器学习", "深度学习",
  "Linux"
]

const extractTechStack = (exp) => {
  if (!exp.description) return
  
  const foundTechs = []
  const desc = exp.description.toLowerCase()
  
  for (const keyword of techKeywords) {
    if (desc.includes(keyword.toLowerCase())) {
      foundTechs.push(keyword)
    }
  }
  
  if (foundTechs.length > 0) {
    const existingTechs = exp.tech_stack ? exp.tech_stack.split(/[,，]/).map(t => t.trim()).filter(t => t) : []
    const allTechs = [...new Set([...existingTechs, ...foundTechs])]
    exp.tech_stack = allTechs.join(", ")
  }
}

const parseSkills = (skillsStr) => {
  try {
    const skills = JSON.parse(skillsStr)
    return Array.isArray(skills) ? skills : []
  } catch (e) {
    return skillsStr ? [skillsStr] : []
  }
}

const parseExperiences = (resume) => {
  // 优先从新的 experiences 字段读取（统一存储）
  let experiencesData = []
  try {
    if (resume.experiences && typeof resume.experiences === 'string') {
      experiencesData = JSON.parse(resume.experiences)
    } else if (Array.isArray(resume.experiences)) {
      experiencesData = resume.experiences
    }
  } catch (e) {
    console.error('解析experiences失败:', e)
  }
  if (Array.isArray(experiencesData) && experiencesData.length > 0) {
    return experiencesData.map(exp => ({
      type: exp.type || 'work',
      company: exp.company || '',
      position: exp.position || '',
      period: exp.period || '',
      description: exp.description || '',
      tech_stack: exp.tech_stack || ''
    }))
  }
  
  // 兼容旧数据：从独立字段读取
  const experiences = []
  // 解析工作经历
  const workExp = parseSkills(resume.work_experience)
  if (Array.isArray(workExp)) {
    workExp.forEach(exp => {
      if (typeof exp === 'object') {
        experiences.push({
          type: 'work',
          company: exp.company || '',
          position: exp.position || '',
          period: exp.period || '',
          description: exp.description || '',
          tech_stack: Array.isArray(exp.technologies) ? exp.technologies.join(', ') : (exp.tech_stack || '')
        })
      }
    })
  }
  // 解析实习经历
  const internExp = parseSkills(resume.internship_experience)
  if (Array.isArray(internExp)) {
    internExp.forEach(exp => {
      if (typeof exp === 'object') {
        experiences.push({
          type: 'internship',
          company: exp.company || '',
          position: exp.position || '',
          period: exp.period || '',
          description: exp.description || '',
          tech_stack: Array.isArray(exp.technologies) ? exp.technologies.join(', ') : (exp.tech_stack || '')
        })
      }
    })
  }
  // 解析项目经历
  const projects = parseSkills(resume.projects)
  if (Array.isArray(projects)) {
    projects.forEach(proj => {
      if (typeof proj === 'object') {
        experiences.push({
          type: 'project',
          company: proj.name || '',
          position: proj.domain || '',
          period: proj.period || '',
          description: proj.description || '',
          tech_stack: Array.isArray(proj.technologies) ? proj.technologies.join(', ') : (proj.tech_stack || '')
        })
      }
    })
  }
  return experiences
}

const loadResumeFromId = async (resumeId) => {
  try {
    console.log('开始加载简历:', resumeId)
    const response = await service.get(`/resume/${resumeId}`)
    console.log('后端返回的数据:', response)
    
    // 和AI解析后完全一样的方式：
    resumeData.value = createEmptyResume()
    resumeData.value.name = response.name || ''
    resumeData.value.phone = response.phone || ''
    resumeData.value.email = response.email || ''
    resumeData.value.school = response.school || ''
    resumeData.value.major = response.major || ''
    resumeData.value.degree = response.degree || ''
    resumeData.value.self_evaluation = response.self_evaluation || ''
    
    // 处理skills - 用AI解析后直接赋值数组
    if (typeof response.skills === 'string') {
      try {
        resumeData.value.skills = JSON.parse(response.skills)
      } catch (e) {
        resumeData.value.skills = []
      }
    } else if (Array.isArray(response.skills)) {
      resumeData.value.skills = response.skills
    }
    
    // 处理experiences - 优先从新的experiences字段读取
    const experiences = []
    const techArrayToString = (techs) => {
      if (Array.isArray(techs)) return techs.join(", ")
      if (typeof techs === "string" && techs) return techs
      return ""
    }
    let experiencesData = []
    if (response.experiences) {
      if (typeof response.experiences === 'string') {
        try {
          experiencesData = JSON.parse(response.experiences)
        } catch (e) {
          experiencesData = []
        }
      } else if (Array.isArray(response.experiences)) {
        experiencesData = response.experiences
      }
    }
    if (Array.isArray(experiencesData) && experiencesData.length > 0) {
      // 确保tech_stack是字符串（兼容新旧数据）
      resumeData.value.experiences = experiencesData.map(exp => ({
        ...exp,
        tech_stack: techArrayToString(exp.tech_stack || exp.technologies)
      }))
    } else {
      // 兼容旧数据：从独立字段读取
      if (response.work_experience) {
        let workExp = []
        if (typeof response.work_experience === 'string') {
          try {
            workExp = JSON.parse(response.work_experience)
          } catch (e) {
            workExp = []
          }
        } else if (Array.isArray(response.work_experience)) {
          workExp = response.work_experience
        }
        if (Array.isArray(workExp)) {
          workExp.forEach(exp => {
            if (typeof exp === 'object') {
              experiences.push({ type: "work", company: exp.company || "", position: exp.position || "", period: exp.period || exp.duration || "", description: exp.description || "", tech_stack: techArrayToString(exp.technologies || exp.tech_stack) })
            }
          })
        }
      }
      if (response.internship_experience) {
        let internExp = []
        if (typeof response.internship_experience === 'string') {
          try {
            internExp = JSON.parse(response.internship_experience)
          } catch (e) {
            internExp = []
          }
        } else if (Array.isArray(response.internship_experience)) {
          internExp = response.internship_experience
        }
        if (Array.isArray(internExp)) {
          internExp.forEach(exp => {
            if (typeof exp === 'object') {
              experiences.push({ type: "internship", company: exp.company || "", position: exp.position || "", period: exp.period || exp.duration || "", description: exp.description || "", tech_stack: techArrayToString(exp.technologies || exp.tech_stack) })
            }
          })
        }
      }
      if (response.projects) {
        let projects = []
        if (typeof response.projects === 'string') {
          try {
            projects = JSON.parse(response.projects)
          } catch (e) {
            projects = []
          }
        } else if (Array.isArray(response.projects)) {
          projects = response.projects
        }
        if (Array.isArray(projects)) {
          projects.forEach(proj => {
            if (typeof proj === 'object') {
              experiences.push({ type: "project", company: proj.name || "", position: proj.domain || "", period: proj.period || proj.duration || "", description: proj.description || "", tech_stack: techArrayToString(proj.technologies || proj.tech_stack) })
            }
          })
        }
      }
      resumeData.value.experiences = experiences
    }
    
    // 处理honors - 优先从新的honors字段读取
    let honorsData = []
    if (response.honors) {
      if (typeof response.honors === 'string') {
        try {
          honorsData = JSON.parse(response.honors)
        } catch (e) {
          honorsData = []
        }
      } else if (Array.isArray(response.honors)) {
        honorsData = response.honors
      }
    }
    if (Array.isArray(honorsData) && honorsData.length > 0) {
      resumeData.value.honors = honorsData
    } else if (response.certificates) {
      // 兼容旧数据
      if (typeof response.certificates === 'string') {
        try {
          resumeData.value.honors = JSON.parse(response.certificates)
        } catch (e) {
          resumeData.value.honors = []
        }
      } else if (Array.isArray(response.certificates)) {
        resumeData.value.honors = response.certificates
      }
    }
    
    console.log('最终的resumeData:', resumeData.value)
    currentResumeId.value = resumeId
  } catch (error) {
    console.error('加载简历失败:', error)
    ElMessage.error('加载简历失败')
    resumeData.value = createEmptyResume()
  }
}

const completionRate = computed(() => {
  if (!resumeData.value) return 0
  const fields = [
    resumeData.value.name,
    resumeData.value.phone,
    resumeData.value.email,
    resumeData.value.school,
    resumeData.value.major,
    resumeData.value.degree,
    resumeData.value.skills.length > 0
  ]
  const completed = fields.filter(f => f).length
  return Math.round((completed / fields.length) * 100)
})

const progressColor = computed(() => {
  if (completionRate.value < 50) return "#f56c6c"
  if (completionRate.value < 80) return "#e6a23c"
  return "#409eff"
})

const handleFileChange = (file) => {
  uploadedFiles.value.push(file)
  ElMessage.success("文件上传成功")
}

const handleFileRemove = (file) => {
  const index = uploadedFiles.value.findIndex(f => f.uid === file.uid)
  if (index > -1) uploadedFiles.value.splice(index, 1)
}

const analyzeFile = async () => {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning("请先上传文件")
    return
  }
  isAnalyzing.value = true
  try {
    const formData = new FormData()
    uploadedFiles.value.forEach(file => formData.append("files", file.raw, file.name))
    const response = await service.post("/resume/extract-resume", formData, { headers: { "Content-Type": "multipart/form-data" } })
    resumeData.value = createEmptyResume()
    const parsed = response
    if (parsed.personalInfo) {
      resumeData.value.name = parsed.personalInfo.name || ""
      resumeData.value.phone = parsed.personalInfo.phone || ""
      resumeData.value.email = parsed.personalInfo.email || ""
    }
    if (parsed.education) {
      resumeData.value.school = parsed.education.school || ""
      resumeData.value.major = parsed.education.major || ""
      resumeData.value.degree = parsed.education.degree || ""
    }
    resumeData.value.skills = parsed.skills || []
    resumeData.value.self_evaluation = parsed.selfEvaluation || ""
    console.log("[DEBUG] AI解析返回结果:", parsed)
    
    const experiences = []
    const techArrayToString = (techs) => {
      if (Array.isArray(techs)) return techs.join(", ")
      if (typeof techs === "string" && techs) return techs
      return ""
    }
    if (Array.isArray(parsed.work_experience)) {
      parsed.work_experience.forEach(exp => experiences.push({ type: "work", company: exp.company || "", position: exp.position || "", period: exp.period || exp.duration || "", description: exp.description || "", tech_stack: techArrayToString(exp.technologies || exp.tech_stack) }))
    }
    if (Array.isArray(parsed.internship_experience)) {
      parsed.internship_experience.forEach(exp => experiences.push({ type: "internship", company: exp.company || "", position: exp.position || "", period: exp.period || exp.duration || "", description: exp.description || "", tech_stack: techArrayToString(exp.technologies || exp.tech_stack) }))
    }
    if (Array.isArray(parsed.projects)) {
      parsed.projects.forEach(proj => experiences.push({ type: "project", company: proj.name || "", position: proj.domain || "", period: proj.period || proj.duration || "", description: proj.description || "", tech_stack: techArrayToString(proj.technologies || proj.tech_stack) }))
    }
    resumeData.value.experiences = experiences
    console.log("[DEBUG] 设置完experiences后:", resumeData.value.experiences)
    
    // 自动为所有有描述的经历自动提取技术栈
    resumeData.value.experiences.forEach(exp => {
      if (exp.description) {
        extractTechStack(exp)
      }
    })
    
    // 设置荣誉奖项
    resumeData.value.honors = parsed.certificates || parsed.honors || []
    console.log("[DEBUG] 设置完honors后:", resumeData.value.honors)
    
    ElMessage.success("AI解析完成，请检查并完善信息")
  } catch (error) {
    ElMessage.error("解析失败，请重试")
    console.error(error)
  } finally {
    isAnalyzing.value = false
  }
}

const addSkillInput = () => {
  showSkillInput.value = true
}

const saveSkill = () => {
  if (newSkill.value.trim()) {
    resumeData.value.skills.push(newSkill.value.trim())
    newSkill.value = ""
  }
  showSkillInput.value = false
}

const cancelSkill = () => {
  newSkill.value = ""
  showSkillInput.value = false
}

const removeSkill = (index) => {
  resumeData.value.skills.splice(index, 1)
}

const addHonor = () => {
  resumeData.value.honors.push({ name: "", issuer: "", date: "" })
}

const removeHonor = (index) => {
  resumeData.value.honors.splice(index, 1)
}

const addExperience = () => {
  resumeData.value.experiences.push({ type: "work", company: "", position: "", period: "", description: "", tech_stack: "" })
}

const removeExperience = (index) => {
  resumeData.value.experiences.splice(index, 1)
}

const saveDraft = () => {
  ElMessage.success("草稿已保存")
  localStorage.setItem("resumeDraft", JSON.stringify(resumeData.value))
  localStorage.setItem("resumeDraftTime", new Date().toLocaleString())
}

const saveResume = async () => {
  if (!resumeData.value) {
    ElMessage.warning("请先填写简历信息")
    return
  }
  if (!resumeData.value.name || !resumeData.value.phone || !resumeData.value.email || !resumeData.value.school || !resumeData.value.major || !resumeData.value.degree) {
    ElMessage.warning("请填写必填信息")
    return
  }
  isSaving.value = true
  try {
    const experiencesValue = resumeData.value.experiences || []
    const honorsValue = resumeData.value.honors || []
    
    if (currentResumeId.value) {
      // 编辑模式 - 使用 PUT 更新接口
      await service.put(`/resume/${currentResumeId.value}`, {
        resume_name: "简历_" + new Date().toLocaleString(),
        name: resumeData.value.name || "",
        age: resumeData.value.age || null,
        phone: resumeData.value.phone || "",
        email: resumeData.value.email || "",
        school: resumeData.value.school || "",
        major: resumeData.value.major || "",
        degree: resumeData.value.degree || "",
        graduation_date: resumeData.value.graduation_date || "",
        skills: JSON.stringify(resumeData.value.skills || []),
        self_evaluation: resumeData.value.self_evaluation || "",
        experiences: JSON.stringify(experiencesValue),
        honors: JSON.stringify(honorsValue),
        work_experience: JSON.stringify(experiencesValue.filter(e => e.type === "work")),
        internship_experience: JSON.stringify(experiencesValue.filter(e => e.type === "internship")),
        projects: JSON.stringify(experiencesValue.filter(e => e.type === "project")),
        certificates: JSON.stringify(honorsValue)
      })
    } else {
      // 新建模式 - 使用 POST 上传接口
      const saveFormData = new FormData()
      saveFormData.append("resume_name", "简历_" + new Date().toLocaleString())
      if (uploadedFiles.value.length > 0) {
        saveFormData.append("file", uploadedFiles.value[0].raw, uploadedFiles.value[0].name)
      }
      saveFormData.append("name", resumeData.value.name || "")
      saveFormData.append("age", resumeData.value.age || "")
      saveFormData.append("phone", resumeData.value.phone || "")
      saveFormData.append("email", resumeData.value.email || "")
      saveFormData.append("school", resumeData.value.school || "")
      saveFormData.append("major", resumeData.value.major || "")
      saveFormData.append("degree", resumeData.value.degree || "")
      saveFormData.append("graduation_date", resumeData.value.graduation_date || "")
      saveFormData.append("skills", JSON.stringify(resumeData.value.skills || []))
      saveFormData.append("self_evaluation", resumeData.value.self_evaluation || "")
      saveFormData.append("experiences", JSON.stringify(experiencesValue))
      saveFormData.append("honors", JSON.stringify(honorsValue))
      saveFormData.append("work_experience", JSON.stringify(experiencesValue.filter(e => e.type === "work")))
      saveFormData.append("internship_experience", JSON.stringify(experiencesValue.filter(e => e.type === "internship")))
      saveFormData.append("projects", JSON.stringify(experiencesValue.filter(e => e.type === "project")))
      saveFormData.append("certificates", JSON.stringify(honorsValue))
      await service.post("/resume/upload", saveFormData, { headers: { "Content-Type": "multipart/form-data" } })
    }
    
    ElMessage.success("简历保存成功！")
    uploadedFiles.value = []
    resumeData.value = null
    currentResumeId.value = null
    localStorage.removeItem("resumeDraft")
    localStorage.removeItem("resumeDraftTime")
  } catch (error) {
    ElMessage.error("保存失败，请重试")
    console.error(error)
  } finally {
    isSaving.value = false
  }
}

const goBack = () => {
  router.push('/job-seeker/resume')
}

onMounted(async () => {
  // 优先检查URL参数
  const resumeId = route.query.resumeId
  const isView = route.query.view === 'true'
  if (resumeId) {
    await loadResumeFromId(resumeId)
    isViewMode.value = isView
    currentResumeId.value = isView ? null : resumeId
  } else {
    // 从localStorage加载草稿
    const draft = localStorage.getItem("resumeDraft")
    if (draft) {
      try {
        resumeData.value = JSON.parse(draft)
      } catch (e) {}
    }
  }
})
</script>

<style scoped>
.header-top { margin-bottom: 16px; }
.back-btn { 
  color: #666; 
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.back-btn:hover {
  color: #409eff;
}

.resume-page { min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 24px 16px; }
.container { max-width: 800px; margin: 0 auto; }
.page-header { text-align: center; margin-bottom: 24px; }
.page-title { font-size: 26px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 0; }
.upload-section { margin-bottom: 20px; }
.upload-card { background: #fff; border-radius: 12px; padding: 28px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); text-align: center; }
.upload-icon { margin-bottom: 12px; color: #409eff; }
.upload-title { font-size: 18px; font-weight: 600; color: #1a1a1a; margin: 0 0 6px 0; }
.upload-desc { font-size: 13px; color: #888; margin: 0 0 16px 0; }
.upload-component { margin-bottom: 14px; }
.form-section { margin-top: 20px; }
.progress-card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 16px; }
.progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.progress-label { font-size: 13px; font-weight: 600; color: #333; }
.progress-value { font-size: 16px; font-weight: 700; color: #409eff; }
.form-section-wrapper { background: #fff; border-radius: 12px; padding: 18px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 16px; }
.section-header { display: flex; align-items: center; margin-bottom: 16px; }
.section-icon { font-size: 22px; margin-right: 10px; }
.section-title-wrapper { display: flex; align-items: center; gap: 8px; flex: 1; }
.section-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; }
.section-badge { font-size: 11px; padding: 1px 6px; border-radius: 3px; }
.section-badge.required { background: #fef0f0; color: #f56c6c; }
.section-badge.optional { background: #f4f4f5; color: #909399; }
.add-btn { color: #409eff; }
.empty-state { text-align: center; color: #999; padding: 20px; background: #f8f9fa; border-radius: 8px; }
.skills-wrapper { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.skill-tag { padding: 6px 12px; font-size: 13px; }
.skill-input { margin-top: 8px; width: 180px; }
.add-skill-btn { color: #409eff; }
.honor-item { padding: 14px; background: #f8f9fa; border-radius: 8px; margin-bottom: 12px; }
.honor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.honor-index { font-size: 12px; font-weight: 600; color: #409eff; }
.experience-card { padding: 16px; background: linear-gradient(135deg, #f8f9fa 0%, #f0f4f8 100%); border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #409eff; }
.exp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.form-footer { display: flex; justify-content: flex-end; gap: 12px; padding-top: 16px; }
.info-group { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0; }
.info-group:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.group-title { font-size: 13px; font-weight: 600; color: #909399; margin: 0 0 12px 0; }
</style>