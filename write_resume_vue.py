
# 写入Vue文件的脚本 - 使用UTF-8无BOM编码
content = '''
<template>
  <div class="resume-page">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">我的简历</h1>
        <p class="page-subtitle">上传简历，AI智能解析，轻松生成结构化简历</p>
      </div>

      <div class="upload-section">
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
        <div class="progress-card">
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
                <span class="section-badge required">必填</span>
              </div>
            </div>
            <div class="section-content">
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="姓名" required>
                    <el-input v-model="resumeData.name" placeholder="请输入姓名" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="电话" required>
                    <el-input v-model="resumeData.phone" placeholder="请输入手机号" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8">
                  <el-form-item label="邮箱" required>
                    <el-input v-model="resumeData.email" placeholder="请输入邮箱" size="large" />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">🎓</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">教育经历</h3>
                <span class="section-badge required">必填</span>
              </div>
            </div>
            <div class="section-content">
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="学校" required>
                    <el-input v-model="resumeData.school" placeholder="请输入学校" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="专业" required>
                    <el-input v-model="resumeData.major" placeholder="请输入专业" size="large" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="6">
                  <el-form-item label="学历" required>
                    <el-select v-model="resumeData.degree" placeholder="请选择学历" size="large" style="width: 100%">
                      <el-option label="高中" value="高中" />
                      <el-option label="大专" value="大专" />
                      <el-option label="本科" value="本科" />
                      <el-option label="硕士" value="硕士" />
                      <el-option label="博士" value="博士" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">💡</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">专业技能</h3>
                <span class="section-badge required">必填</span>
              </div>
            </div>
            <div class="section-content">
              <div class="skills-wrapper">
                <el-tag
                  v-for="(skill, index) in resumeData.skills"
                  :key="index"
                  closable
                  @close="removeSkill(index)"
                  class="skill-tag"
                >{{ skill }}</el-tag>
                <el-button text @click="addSkillInput" class="add-skill-btn">
                  <el-icon><Plus /></el-icon> 添加技能
                </el-button>
              </div>
              <el-input v-if="showSkillInput" v-model="newSkill" @keyup.enter="saveSkill" @blur="cancelSkill" placeholder="输入技能后按回车" class="skill-input" />
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">💼</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">实践经历</h3>
                <span class="section-badge optional">选填</span>
              </div>
              <el-button text @click="addExperience" class="add-btn">
                <el-icon><Plus /></el-icon> 添加经历
              </el-button>
            </div>
            <div class="section-content">
              <div v-if="resumeData.experiences.length === 0" class="empty-state">暂无经历，点击上方添加工作、实习或项目</div>
              <div v-for="(exp, index) in resumeData.experiences" :key="index" class="experience-card">
                <div class="exp-header">
                  <el-select v-model="exp.type" placeholder="类型" size="large" style="width: 120px">
                    <el-option label="全职工作" value="work" />
                    <el-option label="实习" value="internship" />
                    <el-option label="项目" value="project" />
                  </el-select>
                  <el-button link type="danger" @click="removeExperience(index)">删除</el-button>
                </div>
                <el-row :gutter="15">
                  <el-col :xs="24" :md="8">
                    <el-form-item :label="exp.type === 'project' ? '项目名称' : '公司名称'">
                      <el-input v-model="exp.company" :placeholder="exp.type === 'project' ? '请输入项目名称' : '请输入公司名称'" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="8">
                    <el-form-item :label="exp.type === 'project' ? '角色' : '职位'">
                      <el-input v-model="exp.position" :placeholder="exp.type === 'project' ? '请输入角色' : '请输入职位'" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="8">
                    <el-form-item label="时间">
                      <el-input v-model="exp.period" placeholder="如：2021-06 至 2023-03" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24">
                    <el-form-item label="描述">
                      <el-input v-model="exp.description" type="textarea" :rows="3" placeholder="请描述工作内容" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24">
                    <el-form-item label="技术栈">
                      <el-input v-model="exp.tech_stack" placeholder="用逗号分隔" size="large" />
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
                <span class="section-badge optional">选填</span>
              </div>
              <el-button text @click="addHonor" class="add-btn">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            <div class="section-content">
              <div v-if="resumeData.honors.length === 0" class="empty-state">暂无荣誉，点击上方添加</div>
              <div v-for="(honor, index) in resumeData.honors" :key="index" class="honor-item">
                <div class="honor-header">
                  <span class="honor-index">{{ index + 1 }}</span>
                  <el-button link type="danger" @click="removeHonor(index)">删除</el-button>
                </div>
                <el-row :gutter="15">
                  <el-col :xs="24" :md="12">
                    <el-form-item label="荣誉名称">
                      <el-input v-model="honor.name" placeholder="如：校级一等奖学金" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="6">
                    <el-form-item label="颁发方">
                      <el-input v-model="honor.issuer" placeholder="如：清华大学" size="large" />
                    </el-form-item>
                  </el-col>
                  <el-col :xs="24" :md="6">
                    <el-form-item label="时间">
                      <el-input v-model="honor.date" placeholder="如：2023-09" size="large" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>

          <div class="form-section-wrapper">
            <div class="section-header">
              <div class="section-icon">✨</div>
              <div class="section-title-wrapper">
                <h3 class="section-title">自我评价</h3>
                <span class="section-badge optional">选填</span>
              </div>
            </div>
            <div class="section-content">
              <el-input v-model="resumeData.self_evaluation" type="textarea" :rows="4" placeholder="简要介绍一下自己..." size="large" />
            </div>
          </div>

          <div class="form-footer">
            <el-button size="large" @click="saveDraft">
              <el-icon><Document /></el-icon> 保存草稿
            </el-button>
            <el-button type="primary" size="large" :loading="isSaving" @click="saveResume">
              <el-icon><Check /></el-icon> {{ isSaving ? "保存中..." : "生成并保存简历" }}
            </el-button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { Upload, UploadFilled, MagicStick, Plus, Document, Check } from "@element-plus/icons-vue"
import service from "../services/request"

const uploadedFiles = ref([])
const isAnalyzing = ref(false)
const isSaving = ref(false)
const resumeData = ref(null)
const showSkillInput = ref(false)
const newSkill = ref("")

const createEmptyResume = () => ({
  name: "",
  phone: "",
  email: "",
  school: "",
  major: "",
  degree: "",
  skills: [],
  honors: [],
  experiences: [],
  self_evaluation: ""
})

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
    const experiences = []
    if (Array.isArray(parsed.work_experience)) {
      parsed.work_experience.forEach(exp => experiences.push({ type: "work", company: exp.company || "", position: exp.position || "", period: exp.period || "", description: exp.description || "", tech_stack: "" }))
    }
    if (Array.isArray(parsed.internship_experience)) {
      parsed.internship_experience.forEach(exp => experiences.push({ type: "internship", company: exp.company || "", position: exp.position || "", period: exp.period || "", description: exp.description || "", tech_stack: "" }))
    }
    if (Array.isArray(parsed.projects)) {
      parsed.projects.forEach(proj => experiences.push({ type: "project", company: proj.name || "", position: proj.domain || "", period: "", description: proj.description || "", tech_stack: proj.tech_stack || "" }))
    }
    resumeData.value.experiences = experiences
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
}

const saveResume = async () => {
  if (!resumeData.value) {
    ElMessage.warning("请先上传并解析简历")
    return
  }
  if (!resumeData.value.name || !resumeData.value.phone || !resumeData.value.email || !resumeData.value.school || !resumeData.value.major || !resumeData.value.degree) {
    ElMessage.warning("请填写必填信息")
    return
  }
  isSaving.value = true
  try {
    const saveFormData = new FormData()
    saveFormData.append("resume_name", "简历_" + new Date().toLocaleString())
    if (uploadedFiles.value.length > 0) {
      saveFormData.append("file", uploadedFiles.value[0].raw, uploadedFiles.value[0].name)
    }
    saveFormData.append("name", resumeData.value.name || "")
    saveFormData.append("phone", resumeData.value.phone || "")
    saveFormData.append("email", resumeData.value.email || "")
    saveFormData.append("school", resumeData.value.school || "")
    saveFormData.append("major", resumeData.value.major || "")
    saveFormData.append("degree", resumeData.value.degree || "")
    saveFormData.append("skills", JSON.stringify(resumeData.value.skills || []))
    saveFormData.append("self_evaluation", resumeData.value.self_evaluation || "")
    saveFormData.append("experiences", JSON.stringify(resumeData.value.experiences || []))
    saveFormData.append("honors", JSON.stringify(resumeData.value.honors || []))
    const workExps = resumeData.value.experiences.filter(e => e.type === "work")
    const internExps = resumeData.value.experiences.filter(e => e.type === "internship")
    const projects = resumeData.value.experiences.filter(e => e.type === "project")
    saveFormData.append("work_experience", JSON.stringify(workExps))
    saveFormData.append("internship_experience", JSON.stringify(internExps))
    saveFormData.append("projects", JSON.stringify(projects))
    saveFormData.append("certificates", JSON.stringify(resumeData.value.honors || []))
    await service.post("/resume/upload", saveFormData, { headers: { "Content-Type": "multipart/form-data" } })
    ElMessage.success("简历保存成功！")
    uploadedFiles.value = []
    resumeData.value = null
    localStorage.removeItem("resumeDraft")
  } catch (error) {
    ElMessage.error("保存失败，请重试")
    console.error(error)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  const draft = localStorage.getItem("resumeDraft")
  if (draft) {
    try {
      resumeData.value = JSON.parse(draft)
    } catch (e) {}
  }
})
</script>

<style scoped>
.resume-page { min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 40px 20px; }
.container { max-width: 900px; margin: 0 auto; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-title { font-size: 32px; font-weight: 700; color: #1a1a1a; margin: 0 0 10px 0; }
.page-subtitle { font-size: 16px; color: #666; margin: 0; }
.upload-section { margin-bottom: 30px; }
.upload-card { background: #fff; border-radius: 16px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
.upload-icon { margin-bottom: 16px; color: #409eff; }
.upload-title { font-size: 20px; font-weight: 600; color: #1a1a1a; margin: 0 0 8px 0; }
.upload-desc { font-size: 14px; color: #888; margin: 0 0 24px 0; }
.upload-component { margin-bottom: 20px; }
.form-section { margin-top: 30px; }
.progress-card { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 24px; }
.progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.progress-label { font-size: 14px; font-weight: 600; color: #333; }
.progress-value { font-size: 18px; font-weight: 700; color: #409eff; }
.form-section-wrapper { background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 24px; }
.section-header { display: flex; align-items: center; margin-bottom: 24px; }
.section-icon { font-size: 28px; margin-right: 12px; }
.section-title-wrapper { display: flex; align-items: center; gap: 10px; flex: 1; }
.section-title { font-size: 18px; font-weight: 600; color: #1a1a1a; margin: 0; }
.section-badge { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.section-badge.required { background: #fef0f0; color: #f56c6c; }
.section-badge.optional { background: #f4f4f5; color: #909399; }
.add-btn { color: #409eff; }
.empty-state { text-align: center; color: #999; padding: 30px; background: #f8f9fa; border-radius: 12px; }
.skills-wrapper { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.skill-tag { padding: 8px 16px; font-size: 14px; }
.skill-input { margin-top: 10px; width: 200px; }
.add-skill-btn { color: #409eff; }
.honor-item { padding: 20px; background: #f8f9fa; border-radius: 12px; margin-bottom: 16px; }
.honor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.honor-index { font-size: 14px; font-weight: 600; color: #409eff; }
.experience-card { padding: 24px; background: linear-gradient(135deg, #f8f9fa 0%, #f0f4f8 100%); border-radius: 12px; margin-bottom: 16px; border-left: 4px solid #409eff; }
.exp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.form-footer { display: flex; justify-content: flex-end; gap: 16px; padding-top: 24px; }
</style>
'''

# 使用utf-8-sig确保Windows正确识别UTF-8编码
with open("d:/learnspace/ruanjiansai/talent-match-system/frontend/src/views/MyResume.vue", "w", encoding="utf-8-sig") as f:
    f.write(content.strip())
print("文件写入成功")
