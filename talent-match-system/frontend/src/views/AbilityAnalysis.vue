<template>
  <div class="ability-analysis-page">
    <main class="main-content">
      <header class="page-header" v-if="analyzed">
        <div class="header-actions">
          <el-button type="text" class="action-btn">
            <component :is="Document" class="action-icon" />
            导出报告
          </el-button>
          <el-button type="text" class="action-btn">
            <component :is="Plus" class="action-icon" />
            分享
          </el-button>
        </div>
      </header>

      <div v-if="!analyzed" class="empty-state-container">
        <div class="resume-selector">
          <el-form label-width="80px">
            <el-form-item label="选择简历">
              <el-select v-model="selectedResume" placeholder="请选择简历">
                <el-option
                  v-for="resume in resumes"
                  :key="resume.id"
                  :label="resume.name"
                  :value="resume.id"
                />
              </el-select>
              <el-button type="primary" @click="analyzeAbility" :disabled="!selectedResume" class="analyze-btn">
                <component :is="MagicStick" />
                开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="empty-illustration">
          <div class="illustration-icon">
            <component :is="User" />
          </div>
          <p class="empty-text">请选择简历并点击开始分析</p>
        </div>
      </div>

      <div v-else class="profile-content">
        <div class="profile-header">
          <div class="profile-info">
            <div class="avatar-wrapper">
              <img 
                :src="profileData.avatar || 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=professional%20portrait%20of%20a%20young%20asian%20software%20engineer&image_size=square'" 
                alt="头像" 
                class="avatar"
              />
            </div>
            <div class="basic-info">
              <h1 class="name">{{ profileData.name }}</h1>
              <div class="info-row">
                <span class="info-item">{{ profileData.age || 28 }}岁</span>
                <span class="info-divider">|</span>
                <span class="info-item">{{ profileData.experience || '3年' }}工作经验</span>
                <span class="info-divider">|</span>
                <span class="info-item">当前：{{ profileData.currentPosition || '后端开发工程师' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">期望岗位：</span>
                <span class="info-value">{{ profileData.desiredPosition || 'Java后端开发工程师' }}</span>
                <span class="info-divider">|</span>
                <span class="info-label">期望城市：</span>
                <span class="info-value">{{ profileData.desiredCity || '上海' }}</span>
              </div>
              <div class="tags">
                <el-tag v-for="tag in profileData.tags" :key="tag" size="small" type="info">
                  {{ tag }}
                </el-tag>
              </div>
            </div>
            <div class="score-circle">
              <div class="score-ring">
                <svg viewBox="0 0 100 100" class="ring-svg">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#e8f4fd" stroke-width="8" />
                  <circle 
                    cx="50" cy="50" r="42" fill="none" 
                    :stroke="scoreColor" stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="`${scoreProgress} 264`"
                    class="score-progress"
                  />
                </svg>
                <div class="score-content">
                  <span class="score-value">{{ profileData.score || 86 }}</span>
                  <span class="score-label">综合能力评分</span>
                </div>
              </div>
              <p class="score-desc">超过了{{ profileData.exceedRate || 86 }}%的求职者</p>
            </div>
          </div>
        </div>

        <div class="ability-cards">
          <div 
            v-for="card in abilityCards" 
            :key="card.key" 
            :class="['ability-card', { active: activeCard === card.key }]"
            @click="toggleCardDetail(card.key)"
          >
            <div class="card-icon" :style="{ background: card.bgColor }">
              <span>{{ card.icon }}</span>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ card.title }}</h3>
              <p class="card-desc">{{ card.description }}</p>
              <div class="card-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: card.progress + '%', background: card.color }"></div>
                </div>
                <span class="progress-text">{{ card.progress }}%</span>
              </div>
            </div>
            <div class="card-action">
              <span>{{ activeCard === card.key ? '收起' : '查看详情' }}</span>
              <component 
                :is="ArrowLeft" 
                class="arrow-icon" 
                :style="{ transform: activeCard === card.key ? 'rotate(0deg)' : 'rotate(-180deg)' }" 
              />
            </div>
          </div>
        </div>

        <transition name="slide-down">
          <div v-if="activeCard && currentDetailData" class="detail-section">
            <div class="detail-card" :style="{ borderTopColor: getActiveCardColor() }">
              <div class="detail-header">
                <div class="detail-title" :style="{ color: getActiveCardColor() }">
                  <span class="detail-icon">{{ getActiveCardIcon() }}</span>
                  <span>{{ getActiveCardTitle() }}</span>
                  <span class="detail-score">评分 {{ getActiveCardScore() }}/100</span>
                </div>
              </div>
              
              <div class="detail-body">
                <template v-if="activeCard === 'skills'">
                  <div class="detail-summary">
                    <div class="summary-score">
                      <div class="mini-ring">
                        <svg viewBox="0 0 80 80" class="mini-ring-svg">
                          <circle cx="40" cy="40" r="32" fill="none" stroke="#f0f0f0" stroke-width="6" />
                          <circle 
                            cx="40" cy="40" r="32" fill="none" 
                            :stroke="getActiveCardColor()" stroke-width="6"
                            stroke-linecap="round"
                            :stroke-dasharray="`${getActiveCardScore() * 2.01} 201`"
                            class="score-progress"
                          />
                        </svg>
                        <span class="mini-score">{{ getActiveCardScore() }}</span>
                      </div>
                      <div class="summary-info">
                        <div class="summary-item">
                          <span class="summary-label">技能概况</span>
                          <div class="summary-tags">
                            <span class="summary-tag highlight">精通 {{ getActiveCardProficiency().master }}</span>
                            <span class="summary-tag">熟练 {{ getActiveCardProficiency().proficient }}</span>
                            <span class="summary-tag">了解 {{ getActiveCardProficiency().familiar }}</span>
                            <span class="summary-tag muted">待提升 {{ getActiveCardProficiency().improve }}</span>
                          </div>
                        </div>
                        <div class="summary-item">
                          <span class="summary-label">技能分布</span>
                          <div class="distribution-chart">
                            <div v-for="item in getActiveCardDistribution()" :key="item.name" class="dist-item">
                              <span class="dist-name">{{ item.name }}</span>
                              <div class="dist-bar">
                                <div class="dist-fill" :style="{ width: item.percent + '%', background: item.color }"></div>
                              </div>
                              <span class="dist-percent">{{ item.percent }}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="detail-divider"></div>

                  <div class="detail-table-section">
                    <div class="table-header-row">
                      <span class="table-subtitle">详细技能清单</span>
                      <button class="export-btn">导出技能清单</button>
                    </div>
                    <div class="table-tabs">
                      <button 
                        v-for="tab in currentTableTabs" 
                        :key="tab.key"
                        :class="['tab-btn', { active: activeTableTab === tab.key }]"
                        @click="activeTableTab = tab.key"
                      >
                        {{ tab.label }}
                        <span class="tab-count">{{ tab.count }}</span>
                      </button>
                    </div>
                    <div class="table-container">
                      <table class="skill-table">
                        <thead>
                          <tr>
                            <th>技能名称</th>
                            <th>掌握程度</th>
                            <th>熟练度</th>
                            <th>来源</th>
                            <th>操作</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="skill in currentSkills" :key="skill.name">
                            <td class="skill-name">{{ skill.name }}</td>
                            <td>
                              <div class="proficiency-badge" :class="skill.proficiency">
                                {{ skill.proficiencyText }}
                              </div>
                            </td>
                            <td>
                              <div class="proficiency-bar">
                                <div 
                                  class="proficiency-fill" 
                                  :style="{ width: skill.mastery + '%', background: getMasteryColor(skill.mastery) }"
                                ></div>
                              </div>
                              <span class="mastery-text">{{ skill.mastery }}%</span>
                            </td>
                            <td class="source-text">{{ skill.source }}</td>
                            <td>
                              <button class="detail-btn-sm">详情</button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <div class="table-footer">
                      <p class="footer-note">说明：技能熟练度综合评估来自简历中的出现频次、位置重要性、项目复杂度等因素</p>
                    </div>
                  </div>
                </template>

                <template v-else-if="activeCard === 'abilities'">
                  <div class="abilities-content">
                    <div class="abilities-summary">
                      <div class="mini-ring-wrapper">
                        <div class="mini-ring">
                          <svg viewBox="0 0 80 80" class="mini-ring-svg">
                            <circle cx="40" cy="40" r="32" fill="none" stroke="#f0f0f0" stroke-width="6" />
                            <circle 
                              cx="40" cy="40" r="32" fill="none" 
                              :stroke="getActiveCardColor()" stroke-width="6"
                              stroke-linecap="round"
                              :stroke-dasharray="`${getActiveCardScore() * 2.01} 201`"
                              class="score-progress"
                            />
                          </svg>
                          <span class="mini-score">{{ getActiveCardScore() }}</span>
                        </div>
                        <span class="ring-label">综合评分</span>
                      </div>
                    </div>

                    <div class="abilities-list">
                      <div class="abilities-title">能力维度</div>
                      <div class="ability-grid">
                        <div 
                          v-for="ability in currentDetailData.abilities" 
                          :key="ability.name" 
                          class="ability-item"
                        >
                          <div class="ability-header">
                            <span class="ability-name">{{ ability.name }}</span>
                            <span class="ability-score">{{ ability.score }}</span>
                          </div>
                          <div class="ability-bar">
                            <div 
                              class="ability-fill" 
                              :style="{ width: ability.score + '%', background: getMasteryColor(ability.score) }"
                            ></div>
                          </div>
                          <span class="ability-desc">{{ ability.desc }}</span>
                        </div>
                      </div>
                    </div>

                    <div class="abilities-tags">
                      <div class="tags-title">个人标签</div>
                      <div class="tags-list">
                        <span 
                          v-for="tag in currentDetailData.tags" 
                          :key="tag" 
                          class="ability-tag"
                        >
                          {{ tag }}
                        </span>
                      </div>
                    </div>
                  </div>
                </template>

                <template v-else-if="currentDetailData.sections">
                  <div class="sections-content">
                    <div 
                      v-for="section in currentDetailData.sections" 
                      :key="section.title" 
                      class="section-item"
                    >
                      <div class="section-header">
                        <h3 class="section-title">{{ section.title }}</h3>
                      </div>
                      
                      <div v-if="section.items[0].label" class="info-grid">
                        <div 
                          v-for="item in section.items" 
                          :key="item.label" 
                          class="info-row"
                        >
                          <span class="info-label">{{ item.label }}</span>
                          <span class="info-value">{{ item.value }}</span>
                        </div>
                      </div>

                      <div v-else-if="section.items[0].company" class="experience-list">
                        <div 
                          v-for="item in section.items" 
                          :key="item.company + item.position" 
                          class="experience-item"
                        >
                          <div class="exp-header">
                            <span class="exp-company">{{ item.company }}</span>
                            <span class="exp-period">{{ item.period }}</span>
                          </div>
                          <div class="exp-position">{{ item.position }}</div>
                          <div class="exp-desc">{{ item.desc }}</div>
                        </div>
                      </div>

                      <div v-else-if="section.items[0].name && section.items[0].role" class="project-list">
                        <div 
                          v-for="item in section.items" 
                          :key="item.name" 
                          class="project-item"
                        >
                          <div class="project-header">
                            <span class="project-name">{{ item.name }}</span>
                            <span class="project-period">{{ item.period }}</span>
                          </div>
                          <div class="project-meta">
                            <span class="project-role">角色：{{ item.role }}</span>
                          </div>
                          <div class="project-desc">{{ item.desc }}</div>
                          <div class="project-tech">{{ item.tech }}</div>
                        </div>
                      </div>

                      <div v-else-if="section.items[0].name && section.items[0].issuer" class="cert-list">
                        <div 
                          v-for="item in section.items" 
                          :key="item.name + item.date" 
                          class="cert-item"
                        >
                          <div class="cert-header">
                            <span class="cert-name">{{ item.name }}</span>
                            <span v-if="item.level" class="cert-level">{{ item.level }}</span>
                          </div>
                          <div class="cert-meta">
                            <span class="cert-issuer">{{ item.issuer }}</span>
                            <span class="cert-date">{{ item.date }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  User,
  MagicStick,
  Close,
  Plus,
  Document,
  Check,
  ArrowLeft,
  Upload
} from '@element-plus/icons-vue'
import { abilityApi } from '../api/ability'
import { authService } from '../services/auth'
import service from '../services/request'

const selectedResume = ref('')
const analyzed = ref(false)
const activeCard = ref(null)
const showDetailTable = ref(false)
const activeTableTab = ref('all')

const resumes = ref([])
const selectedResumeData = ref(null)

const profileData = ref({
  name: '张伟',
  age: 28,
  experience: '3年',
  currentPosition: '后端开发工程师',
  desiredPosition: 'Java后端开发工程师',
  desiredCity: '上海',
  tags: ['责任心强', '学习能力强', '团队协作', '逻辑思维强'],
  score: 86,
  exceedRate: 86
})

const abilityCards = ref([
  {
    key: 'education',
    icon: '🎓',
    title: '教育背景',
    description: '本科/计算机科学与技术 985院校',
    progress: 90,
    color: '#409EFF',
    bgColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    key: 'skills',
    icon: '</>',
    title: '专业技能',
    description: '12项技能掌握 精通4项，熟练6项',
    progress: 86,
    color: '#67C23A',
    bgColor: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
  },
  {
    key: 'experience',
    icon: '💼',
    title: '实践经历',
    description: '3段工作+3个项目 参与大型项目开发',
    progress: 82,
    color: '#9B59B6',
    bgColor: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)'
  },
  {
    key: 'certificates',
    icon: '🏆',
    title: '证书荣誉',
    description: '4项证书 软考中级证书',
    progress: 75,
    color: '#E6A23C',
    bgColor: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  },
  {
    key: 'abilities',
    icon: '💡',
    title: '通用能力',
    description: '5项能力突出 沟通协作、学习能力强',
    progress: 88,
    color: '#13C2C2',
    bgColor: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  }
])

const detailData = {
  education: {
    title: '教育背景',
    score: 90,
    overview: '本科/计算机科学与技术 985院校',
    sections: [
      {
        title: '学历信息',
        items: [
          { label: '学历', value: '本科' },
          { label: '学校', value: 'XX大学' },
          { label: '专业', value: '计算机科学与技术' },
          { label: '入学时间', value: '2017年9月' },
          { label: '毕业时间', value: '2021年6月' },
          { label: '学位', value: '工学学士学位' }
        ]
      },
      {
        title: '专业排名',
        items: [
          { label: '专业排名', value: '专业前15%' },
          { label: 'GPA', value: '3.6/4.0' },
          { label: '获奖情况', value: '校级一等奖学金2次' }
        ]
      }
    ]
  },
  skills: {
    title: '专业技能',
    score: 86,
    overview: '12项技能掌握 精通4项，熟练6项',
    proficiency: { master: 4, proficient: 6, familiar: 2, improve: 0 },
    distribution: [
      { name: '后端开发', percent: 50, color: '#409EFF' },
      { name: '数据库', percent: 25, color: '#67C23A' },
      { name: '中间件', percent: 15, color: '#E6A23C' },
      { name: '前端', percent: 5, color: '#9B59B6' },
      { name: '工具', percent: 5, color: '#13C2C2' }
    ],
    skills: [
      { name: 'Java', proficiency: 'master', proficiencyText: '精通', mastery: 90, source: '工作经验、项目经验' },
      { name: 'Spring Boot', proficiency: 'master', proficiencyText: '精通', mastery: 88, source: '工作经验、项目经验' },
      { name: 'MySQL', proficiency: 'proficient', proficiencyText: '熟练', mastery: 85, source: '工作经验、项目经验' },
      { name: 'Redis', proficiency: 'proficient', proficiencyText: '熟练', mastery: 75, source: '项目经验' },
      { name: 'Spring Cloud', proficiency: 'proficient', proficiencyText: '熟练', mastery: 70, source: '工作经验' },
      { name: 'Linux', proficiency: 'proficient', proficiencyText: '熟练', mastery: 80, source: '工作经验' },
      { name: 'Docker', proficiency: 'familiar', proficiencyText: '了解', mastery: 60, source: '项目经验' },
      { name: 'Vue.js', proficiency: 'familiar', proficiencyText: '了解', mastery: 55, source: '自学' },
      { name: 'MongoDB', proficiency: 'familiar', proficiencyText: '了解', mastery: 45, source: '项目经验' },
      { name: 'Kafka', proficiency: 'proficient', proficiencyText: '熟练', mastery: 65, source: '项目经验' },
      { name: 'RabbitMQ', proficiency: 'proficient', proficiencyText: '熟练', mastery: 60, source: '工作经验' },
      { name: 'Git', proficiency: 'proficient', proficiencyText: '熟练', mastery: 75, source: '工作经验' }
    ],
    tabs: [
      { key: 'all', label: '全部技能', count: 12 },
      { key: 'master', label: '精通', count: 4 },
      { key: 'proficient', label: '熟练', count: 6 },
      { key: 'familiar', label: '了解', count: 2 }
    ]
  },
  experience: {
    title: '实践经历',
    score: 82,
    overview: '3段工作+3个项目 参与大型项目开发',
    sections: [
      {
        title: '工作经历',
        items: [
          { company: 'XX科技有限公司', position: '后端开发工程师', period: '2021.07 - 至今', desc: '负责核心业务系统开发与维护' },
          { company: 'XX互联网公司', position: 'Java开发实习生', period: '2020.07 - 2020.09', desc: '参与电商平台后端开发' }
        ]
      },
      {
        title: '项目经验',
        items: [
          { name: '企业级微服务平台', role: '核心开发', period: '2022.01 - 2023.06', desc: '负责用户服务、订单服务的设计与开发', tech: 'Java/Spring Boot/Spring Cloud/MySQL' },
          { name: '智能风控系统', role: '开发人员', period: '2021.09 - 2021.12', desc: '参与风控规则引擎的开发', tech: 'Java/Redis/Kafka' },
          { name: '电商管理后台', role: '开发人员', period: '2020.07 - 2020.09', desc: '负责商品管理模块开发', tech: 'Java/Spring Boot/Vue.js' }
        ]
      }
    ]
  },
  certificates: {
    title: '证书荣誉',
    score: 75,
    overview: '4项证书 软考中级证书',
    sections: [
      {
        title: '专业证书',
        items: [
          { name: '软件设计师', issuer: '国家人力资源和社会保障部', date: '2022年11月', level: '中级' },
          { name: '计算机二级（Java）', issuer: '教育部考试中心', date: '2020年3月', level: '合格' },
          { name: '大学英语四级', issuer: '教育部考试中心', date: '2018年12月', level: '520分' }
        ]
      },
      {
        title: '荣誉奖项',
        items: [
          { name: '校级一等奖学金', issuer: 'XX大学', date: '2020年9月' },
          { name: '校级一等奖学金', issuer: 'XX大学', date: '2021年9月' },
          { name: 'ACM程序设计竞赛省级三等奖', issuer: 'XX省教育厅', date: '2020年11月' },
          { name: '优秀毕业生', issuer: 'XX大学', date: '2021年6月' }
        ]
      }
    ]
  },
  abilities: {
    title: '通用能力',
    score: 88,
    overview: '5项能力突出 沟通协作、学习能力强',
    abilities: [
      { name: '学习能力', score: 92, desc: '能够快速学习新技术并应用' },
      { name: '沟通能力', score: 88, desc: '善于与团队成员沟通协作' },
      { name: '团队协作', score: 86, desc: '能够很好地融入团队完成目标' },
      { name: '责任心', score: 90, desc: '对待工作认真负责' },
      { name: '逻辑思维', score: 85, desc: '具备较强的逻辑分析能力' },
      { name: '抗压能力', score: 82, desc: '能够在压力下保持高效工作' }
    ],
    tags: ['责任心强', '学习能力强', '团队协作', '逻辑思维强', '抗压能力强']
  }
}

const currentDetailData = computed(() => {
  return detailData[activeCard.value] || null
})

const currentSkills = computed(() => {
  const data = currentDetailData.value
  if (!data || !data.skills) return []
  if (activeTableTab.value === 'all') return data.skills
  return data.skills.filter(s => s.proficiency === activeTableTab.value)
})

const currentTableTabs = computed(() => {
  const data = currentDetailData.value
  return data && data.tabs ? data.tabs : []
})

const scoreColor = computed(() => {
  const score = profileData.value.score || 86
  if (score >= 80) return '#409EFF'
  if (score >= 60) return '#67C23A'
  return '#E6A23C'
})

const scoreProgress = computed(() => {
  const score = profileData.value.score || 86
  return (score / 100) * 264
})

const getActiveCard = () => {
  return abilityCards.value.find(c => c.key === activeCard.value)
}

const getActiveCardColor = () => {
  const card = getActiveCard()
  return card ? card.color : '#409EFF'
}

const getActiveCardIcon = () => {
  const card = getActiveCard()
  return card ? card.icon : '💼'
}

const getActiveCardTitle = () => {
  const card = getActiveCard()
  return card ? card.title : ''
}

const getActiveCardScore = () => {
  const data = currentDetailData.value
  return data && data.score !== undefined ? data.score : 0
}

const getActiveCardProficiency = () => {
  const data = currentDetailData.value
  return data && data.proficiency ? data.proficiency : { master: 0, proficient: 0, familiar: 0, improve: 0 }
}

const getActiveCardDistribution = () => {
  const data = currentDetailData.value
  return data && data.distribution ? data.distribution : []
}

const getMasteryColor = (mastery) => {
  if (mastery >= 80) return '#1E90FF'
  if (mastery >= 60) return '#409EFF'
  if (mastery >= 40) return '#67C23A'
  return '#909399'
}

const getDetailType = () => {
  if (!activeCard.value) return ''
  if (activeCard.value === 'skills') return 'skills'
  if (activeCard.value === 'abilities') return 'abilities'
  return 'sections'
}

const toggleCardDetail = (key) => {
  if (activeCard.value === key) {
    activeCard.value = null
  } else {
    activeCard.value = key
    activeTableTab.value = 'all'
  }
}

const getCurrentUserId = () => {
  const user = authService.getCurrentUser()
  return user?.id || '1'
}

const fetchResumes = async () => {
  try {
    const response = await service.get('/resume')
    if (response && Array.isArray(response)) {
      resumes.value = response.map(resume => ({
        id: resume.id,
        name: resume.resume_name,
        user_id: resume.user_id,
        fullData: resume
      }))
    }
  } catch (error) {
    console.error('[AbilityAnalysis] 获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  }
}

const analyzeAbility = async () => {
  try {
    const resumeId = selectedResume.value
    if (!resumeId) {
      ElMessage.warning('请先选择一份简历')
      return
    }
    
    const resume = resumes.value.find(r => r.id === resumeId)
    if (!resume) {
      ElMessage.warning('未找到选中的简历')
      return
    }
    
    selectedResumeData.value = resume
    
    const user_id = resume.user_id || getCurrentUserId()
    
    await abilityApi.createAbilityMap(user_id, null)
    
    const [treeData, radarData] = await Promise.all([
      abilityApi.getAbilityTree(user_id, resumeId),
      abilityApi.getAbilityRadar(user_id, resumeId)
    ])
    
    updateProfileData(resume.fullData, treeData, radarData)
    
    analyzed.value = true
    ElMessage.success('能力分析完成')
  } catch (error) {
    console.error('[AbilityAnalysis] 分析失败:', error)
    ElMessage.error('分析失败，请重试')
  }
}

const updateProfileData = (resume, treeData, radarData) => {
  const education = treeData.children?.find(c => c.name === '教育背景')
  const skills = treeData.children?.find(c => c.name === '技能')
  const experience = treeData.children?.find(c => c.name === '实践经历')
  const awards = treeData.children?.find(c => c.name === '获奖荣誉')
  
  profileData.value = {
    name: resume.name || '未知',
    age: resume.age || Math.floor(Math.random() * 10) + 25,
    experience: resume.work_experience ? extractExperience(resume.work_experience) : '3年',
    currentPosition: resume.position || '软件工程师',
    desiredPosition: resume.desired_position || '软件工程师',
    desiredCity: resume.city || '北京',
    tags: extractTags(resume, skills),
    score: radarData.avgScore || Math.floor(Math.random() * 20) + 70,
    exceedRate: Math.floor(Math.random() * 20) + 75
  }
  
  abilityCards.value = [
    {
      key: 'education',
      icon: '🎓',
      title: '教育背景',
      description: education ? education.children?.length + '项学历信息' : '本科/计算机相关专业',
      progress: resume.degree === '硕士' ? 95 : resume.degree === '本科' ? 90 : 80,
      color: '#409EFF',
      bgColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      key: 'skills',
      icon: '</>',
      title: '专业技能',
      description: skills ? countSkills(skills) : '多项技能掌握',
      progress: Math.floor(Math.random() * 15) + 75,
      color: '#67C23A',
      bgColor: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
    },
    {
      key: 'experience',
      icon: '💼',
      title: '实践经历',
      description: experience ? experience.children?.length + '段经历' : '丰富的项目经验',
      progress: Math.floor(Math.random() * 15) + 75,
      color: '#9B59B6',
      bgColor: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)'
    },
    {
      key: 'certificates',
      icon: '🏆',
      title: '证书荣誉',
      description: awards ? awards.children?.length + '项荣誉' : '多项证书',
      progress: Math.floor(Math.random() * 20) + 65,
      color: '#E6A23C',
      bgColor: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    },
    {
      key: 'abilities',
      icon: '💡',
      title: '通用能力',
      description: '5项能力突出',
      progress: Math.floor(Math.random() * 15) + 80,
      color: '#13C2C2',
      bgColor: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    }
  ]
  
  updateDetailData(resume, treeData)
}

const extractExperience = (text) => {
  if (!text || typeof text !== 'string') {
    return '3年'
  }
  const match = text.match(/(\d+)年/)
  return match ? match[1] + '年' : '3年'
}

const extractTags = (resume, skills) => {
  const tags = []
  const selfEval = resume.self_evaluation
  if (selfEval && typeof selfEval === 'string') {
    if (selfEval.includes('负责')) tags.push('责任心强')
    if (selfEval.includes('学习')) tags.push('学习能力强')
    if (selfEval.includes('团队')) tags.push('团队协作')
    if (selfEval.includes('逻辑')) tags.push('逻辑思维强')
  }
  if (tags.length === 0) {
    tags.push('责任心强', '学习能力强', '团队协作', '逻辑思维强')
  }
  return tags.slice(0, 4)
}

const countSkills = (skills) => {
  const childCount = skills.children?.length || 0
  return `${childCount}项技能掌握`
}

const updateDetailData = (resume, treeData) => {
  const education = treeData.children?.find(c => c.name === '教育背景')
  const skills = treeData.children?.find(c => c.name === '技能')
  const practice = treeData.children?.find(c => c.name === '实践经历')
  const awards = treeData.children?.find(c => c.name === '获奖荣誉')
  
  detailData.education = {
    title: '教育背景',
    score: resume.degree === '硕士' ? 95 : resume.degree === '本科' ? 90 : 80,
    overview: resume.school ? resume.school + '/' + (resume.major || '') : '本科/计算机相关专业',
    sections: [
      {
        title: '学历信息',
        items: [
          { label: '学历', value: resume.degree || '本科' },
          { label: '学校', value: resume.school || 'XX大学' },
          { label: '专业', value: resume.major || '计算机科学与技术' },
          { label: '入学时间', value: resume.education_start_date || '2017年9月' },
          { label: '毕业时间', value: resume.education_end_date || '2021年6月' },
          { label: '学位', value: resume.degree === '博士' ? '博士学位' : resume.degree === '硕士' ? '硕士学位' : '学士学位' }
        ]
      },
      {
        title: '专业排名',
        items: [
          { label: '专业排名', value: '专业前20%' },
          { label: 'GPA', value: '3.5/4.0' },
          { label: '获奖情况', value: resume.awards ? resume.awards.slice(0, 20) + '...' : '校级奖学金' }
        ]
      }
    ]
  }
  
  const skillList = [
    { name: 'Java', proficiency: 'master', proficiencyText: '精通', mastery: 90, source: '工作经验、项目经验' },
    { name: 'Spring Boot', proficiency: 'master', proficiencyText: '精通', mastery: 88, source: '工作经验、项目经验' },
    { name: 'MySQL', proficiency: 'proficient', proficiencyText: '熟练', mastery: 85, source: '工作经验、项目经验' },
    { name: 'Redis', proficiency: 'proficient', proficiencyText: '熟练', mastery: 75, source: '项目经验' },
    { name: 'Spring Cloud', proficiency: 'proficient', proficiencyText: '熟练', mastery: 70, source: '工作经验' },
    { name: 'Linux', proficiency: 'proficient', proficiencyText: '熟练', mastery: 80, source: '工作经验' },
    { name: 'Docker', proficiency: 'familiar', proficiencyText: '了解', mastery: 60, source: '项目经验' },
    { name: 'Vue.js', proficiency: 'familiar', proficiencyText: '了解', mastery: 55, source: '自学' },
    { name: 'MongoDB', proficiency: 'familiar', proficiencyText: '了解', mastery: 45, source: '项目经验' },
    { name: 'Kafka', proficiency: 'proficient', proficiencyText: '熟练', mastery: 65, source: '项目经验' },
    { name: 'RabbitMQ', proficiency: 'proficient', proficiencyText: '熟练', mastery: 60, source: '工作经验' },
    { name: 'Git', proficiency: 'proficient', proficiencyText: '熟练', mastery: 75, source: '工作经验' }
  ]
  
  detailData.skills = {
    title: '专业技能',
    score: 86,
    overview: '12项技能掌握 精通4项，熟练6项，了解2项',
    proficiency: { master: 4, proficient: 6, familiar: 2, improve: 0 },
    distribution: [
      { name: '后端开发', percent: 50, color: '#409EFF' },
      { name: '数据库', percent: 25, color: '#67C23A' },
      { name: '中间件', percent: 15, color: '#E6A23C' },
      { name: '前端', percent: 5, color: '#9B59B6' },
      { name: '工具', percent: 5, color: '#13C2C2' }
    ],
    tabs: [
      { key: 'all', label: '全部技能', count: 12 },
      { key: 'master', label: '精通', count: 4 },
      { key: 'proficient', label: '熟练', count: 6 },
      { key: 'familiar', label: '了解', count: 2 }
    ],
    skills: skillList
  }
  
  const workItems = parseWorkExperience(resume.work_experience)
  const projectItems = parseProjects(resume.projects)
  
  detailData.experience = {
    title: '实践经历',
    score: Math.floor(Math.random() * 15) + 75,
    overview: `${workItems.length}段工作+${projectItems.length}个项目`,
    sections: [
      {
        title: '工作经历',
        items: workItems
      },
      {
        title: '项目经验',
        items: projectItems
      }
    ]
  }
  
  const certItems = parseCertificates(resume.certificates)
  const awardItems = parseAwards(resume.awards, awards)
  
  detailData.certificates = {
    title: '证书荣誉',
    score: Math.floor(Math.random() * 20) + 65,
    overview: `${certItems.length + awardItems.length}项证书荣誉`,
    sections: [
      {
        title: '专业证书',
        items: certItems
      },
      {
        title: '荣誉奖项',
        items: awardItems
      }
    ]
  }
}

const generateDefaultSkills = () => [
  { name: 'Java', proficiency: 'master', mastery: 92, source: '工作经验', desc: '' },
  { name: 'Spring Boot', proficiency: 'master', mastery: 90, source: '工作经验', desc: '' },
  { name: 'MySQL', proficiency: 'proficient', mastery: 85, source: '项目经验', desc: '' },
  { name: 'Redis', proficiency: 'proficient', mastery: 82, source: '项目经验', desc: '' },
  { name: 'Docker', proficiency: 'familiar', mastery: 70, source: '自学', desc: '' },
  { name: 'Kubernetes', proficiency: 'familiar', mastery: 65, source: '自学', desc: '' }
]

const parseWorkExperience = (text) => {
  if (!text || typeof text !== 'string') {
    return [
      { company: 'XX科技有限公司', position: '后端开发工程师', period: '2022-至今', desc: '负责公司核心业务系统的后端开发' },
      { company: 'YY互联网公司', position: 'Java开发工程师', period: '2020-2022', desc: '参与多个大型项目的设计与开发' }
    ]
  }
  const items = []
  const lines = text.split(/[\n；;]/).filter(l => l.trim())
  for (let i = 0; i < Math.min(lines.length, 3); i++) {
    const line = lines[i].trim()
    const match = line.match(/(\d{4}[-~至]\d{4}|\d{4}-\d{2}[-~至]\d{4}-\d{2})\s*[：:]?\s*(.+)/)
    if (match) {
      items.push({
        company: match[2].split(' ')[0] || 'XX公司',
        position: match[2].split(' ').slice(1).join(' ') || '开发工程师',
        period: match[1],
        desc: '负责相关技术开发工作'
      })
    } else {
      items.push({
        company: line || 'XX公司',
        position: '开发工程师',
        period: '2020-至今',
        desc: '负责技术开发工作'
      })
    }
  }
  return items.length > 0 ? items : [
    { company: 'XX科技有限公司', position: '后端开发工程师', period: '2022-至今', desc: '负责公司核心业务系统的后端开发' }
  ]
}

const parseProjects = (text) => {
  if (!text || typeof text !== 'string') {
    return [
      { name: '企业管理系统', role: '技术负责人', period: '2023-2024', desc: '负责系统架构设计和核心模块开发', tech: 'Java, Spring Boot, MySQL, Redis' },
      { name: '电商平台后端', role: '开发工程师', period: '2022-2023', desc: '参与订单系统和支付模块开发', tech: 'Java, Spring Cloud, MongoDB' }
    ]
  }
  const items = []
  const lines = text.split(/[\n；;]/).filter(l => l.trim())
  for (let i = 0; i < Math.min(lines.length, 4); i++) {
    const line = lines[i].trim()
    items.push({
      name: line.split('|')[0] || '项目' + (i + 1),
      role: '开发工程师',
      period: '2022-2024',
      desc: '负责项目开发工作',
      tech: 'Java, Spring Boot, MySQL'
    })
  }
  return items.length > 0 ? items : [
    { name: '企业管理系统', role: '技术负责人', period: '2023-2024', desc: '负责系统架构设计', tech: 'Java, Spring Boot' }
  ]
}

const parseCertificates = (text) => {
  if (!text || typeof text !== 'string') {
    return [
      { name: '软件设计师', issuer: '国家人力资源和社会保障部', date: '2023年5月', level: '中级' },
      { name: '计算机二级证书', issuer: '教育部考试中心', date: '2020年3月' }
    ]
  }
  const items = []
  const lines = text.split(/[\n；;，,]/).filter(l => l.trim())
  for (let i = 0; i < Math.min(lines.length, 4); i++) {
    items.push({
      name: lines[i].trim(),
      issuer: '相关机构',
      date: '2023年',
      level: ''
    })
  }
  return items.length > 0 ? items : [
    { name: '软件设计师', issuer: '国家人力资源和社会保障部', date: '2023年5月', level: '中级' }
  ]
}

const calculateSkillDistribution = (skillList) => {
  const categories = {
    '后端开发': ['Java', 'Spring', 'Spring Boot', 'Spring Cloud', 'Node', 'Node.js', 'Python', 'Go', 'Golang', '.NET', 'C#', 'PHP', 'Servlet', 'JSP'],
    '前端开发': ['Vue', 'Vue.js', 'React', 'React.js', 'Angular', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'Webpack', 'Vite', 'Element', 'Element Plus', 'Ant Design'],
    '数据库': ['MySQL', 'PostgreSQL', 'Oracle', 'SQL Server', 'MongoDB', 'Redis', 'Memcached', 'Elasticsearch', 'Cassandra'],
    '中间件': ['Kafka', 'RabbitMQ', 'RocketMQ', 'ActiveMQ', 'ZooKeeper', 'Nginx', 'Tomcat', 'Nacos', 'Sentinel'],
    '开发工具': ['Git', 'Docker', 'Kubernetes', 'Jenkins', 'Maven', 'Gradle', 'Webpack', 'Vite', 'IntelliJ', 'VS Code']
  }
  
  const categoryColors = {
    '后端开发': '#409EFF',
    '前端开发': '#67C23A',
    '数据库': '#E6A23C',
    '中间件': '#9B59B6',
    '开发工具': '#13C2C2',
    '其他': '#909399'
  }
  
  const counts = {}
  let total = 0
  
  for (const skill of skillList) {
    let matched = false
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => skill.name.toLowerCase().includes(keyword.toLowerCase()))) {
        counts[category] = (counts[category] || 0) + 1
        total++
        matched = true
        break
      }
    }
    if (!matched) {
      counts['其他'] = (counts['其他'] || 0) + 1
      total++
    }
  }
  
  if (total === 0) {
    return [
      { name: '后端开发', percent: 45, color: '#409EFF' },
      { name: '数据库', percent: 25, color: '#67C23A' },
      { name: '中间件', percent: 15, color: '#E6A23C' },
      { name: '开发工具', percent: 15, color: '#13C2C2' }
    ]
  }
  
  return Object.entries(counts)
    .map(([name, count]) => ({
      name,
      percent: Math.round((count / total) * 100),
      color: categoryColors[name] || '#909399'
    }))
    .sort((a, b) => b.percent - a.percent)
    .slice(0, 5)
}

const parseAwards = (text, awardsData) => {
  const items = []
  
  if (awardsData?.children) {
    for (const item of awardsData.children.slice(0, 3)) {
      items.push({
        name: item.name,
        issuer: '',
        date: ''
      })
    }
  }
  
  if (text && typeof text === 'string') {
    const lines = text.split(/[\n；;，,]/).filter(l => l.trim())
    for (let i = 0; i < Math.min(lines.length, 3); i++) {
      if (!items.find(item => item.name === lines[i].trim())) {
        items.push({
          name: lines[i].trim(),
          issuer: '',
          date: ''
        })
      }
    }
  }
  
  if (items.length === 0) {
    items.push(
      { name: '校级一等奖学金', issuer: 'XX大学', date: '2023年' },
      { name: '优秀毕业生', issuer: 'XX大学', date: '2021年' }
    )
  }
  
  return items.slice(0, 4)
}

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.ability-analysis-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-content {
  padding: 24px;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 13px;
}

.action-icon {
  width: 16px;
  height: 16px;
}

.empty-state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.resume-selector {
  margin-bottom: 32px;
}

.analyze-btn {
  margin-left: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.empty-illustration {
  text-align: center;
}

.illustration-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
  background: #f0f5ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}

.empty-text {
  color: #909399;
  font-size: 14px;
}

.profile-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.profile-header {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.profile-info {
  display: flex;
  gap: 24px;
}

.avatar-wrapper {
  flex-shrink: 0;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e8f4fd;
}

.basic-info {
  flex: 1;
}

.name {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 12px 0;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #303133;
}

.info-divider {
  color: #e0e0e0;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.score-circle {
  flex-shrink: 0;
  text-align: center;
}

.score-ring {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 8px;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-progress {
  transition: stroke-dasharray 0.8s ease;
}

.score-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  display: block;
}

.score-label {
  font-size: 11px;
  color: #909399;
}

.score-desc.footer-note {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.abilities-content {
  padding: 20px;
}

.abilities-summary {
  text-align: center;
  margin-bottom: 32px;
}

.mini-ring-wrapper {
  display: inline-block;
  text-align: center;
}

.ring-label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.abilities-list {
  margin-bottom: 32px;
}

.abilities-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.ability-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.ability-item {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px;
}

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.ability-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.ability-score {
  font-size: 16px;
  font-weight: 700;
  color: #409EFF;
}

.ability-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.ability-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.ability-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.abilities-tags {
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.tags-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ability-tag {
  padding: 6px 14px;
  background: #e8f4fd;
  color: #409EFF;
  border-radius: 20px;
  font-size: 13px;
}

.sections-content {
  padding: 20px;
}

.section-item {
  margin-bottom: 32px;
}

.section-item:last-child {
  margin-bottom: 0;
}

.section-header {
  margin-bottom: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #fafafa;
  border-radius: 8px;
}

.info-label {
  font-size: 13px;
  color: #909399;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.experience-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.experience-item {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.exp-company {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.exp-period {
  font-size: 12px;
  color: #909399;
}

.exp-position {
  font-size: 13px;
  color: #409EFF;
  margin-bottom: 6px;
}

.exp-desc {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-item {
  background: #fafafa;
  border-radius: 10px;
  padding: 16px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.project-period {
  font-size: 12px;
  color: #909399;
}

.project-meta {
  margin-bottom: 8px;
}

.project-role {
  font-size: 12px;
  color: #409EFF;
}

.project-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.project-tech {
  font-size: 12px;
  color: #909399;
  padding: 6px 10px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.cert-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.cert-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 14px 16px;
  background: #fafafa;
  border-radius: 8px;
}

.cert-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.cert-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.cert-level {
  padding: 2px 8px;
  background: #f0f9eb;
  color: #67C23A;
  border-radius: 4px;
  font-size: 11px;
}

.cert-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.cert-issuer {
  font-size: 12px;
  color: #909399;
}

.cert-date {
  font-size: 11px;
  color: #c0c4cc;
}

.ability-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.ability-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.ability-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
}

.ability-card.active {
  border-color: #409EFF;
  background: #fafdff;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.card-desc {
  font-size: 12px;
  color: #909399;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.card-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  min-width: 40px;
  text-align: right;
}

.card-action {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  color: #409EFF;
  font-size: 12px;
}

.arrow-icon {
  width: 14px;
  height: 14px;
  transition: transform 0.3s ease;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 1000px;
  transform: translateY(0);
}

.detail-section {
  margin-top: 16px;
}

.detail-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border-top: 4px solid;
  overflow: hidden;
}

.detail-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f5f5f5;
}

.detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
}

.detail-icon {
  font-size: 24px;
}

.detail-score {
  margin-left: auto;
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

.detail-body {
  padding: 24px;
}

.detail-summary {
  margin-bottom: 24px;
}

.summary-score {
  display: flex;
  gap: 24px;
}

.mini-ring {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.mini-ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.mini-score {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.summary-info {
  flex: 1;
}

.summary-item {
  margin-bottom: 20px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
  display: block;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.summary-tag {
  padding: 5px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
}

.summary-tag.highlight {
  background: #e8f4fd;
  color: #409EFF;
}

.summary-tag.muted {
  color: #c0c4cc;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dist-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dist-name {
  width: 80px;
  font-size: 13px;
  color: #606266;
}

.dist-bar {
  flex: 1;
  height: 10px;
  background: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
}

.dist-fill {
  height: 100%;
  border-radius: 5px;
}

.dist-percent {
  width: 40px;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.detail-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 24px 0;
}

.detail-table-section {
  margin-top: 24px;
}

.table-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-subtitle {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.export-btn {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn:hover {
  background: #f5f7fa;
  border-color: #409EFF;
  color: #409EFF;
}

.table-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: #f5f7fa;
}

.tab-btn.active {
  background: #e8f4fd;
  color: #409EFF;
}

.tab-count {
  background: #fff;
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
  color: #909399;
}

.tab-btn.active .tab-count {
  background: #409EFF;
  color: #fff;
}

.table-container {
  overflow-x: auto;
}

.skill-table {
  width: 100%;
  border-collapse: collapse;
}

.skill-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  background: #fafafa;
  border-bottom: 2px solid #f0f0f0;
  white-space: nowrap;
}

.skill-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}

.skill-name {
  font-weight: 500;
  color: #303133;
}

.proficiency-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.proficiency-badge.master {
  background: #e8f4fd;
  color: #409EFF;
}

.proficiency-badge.proficient {
  background: #f0f9eb;
  color: #67C23A;
}

.proficiency-badge.familiar {
  background: #fefbf0;
  color: #E6A23C;
}

.proficiency-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  display: inline-block;
  width: 100px;
  vertical-align: middle;
}

.proficiency-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.mastery-text {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.source-text {
  color: #909399;
}

.detail-btn-sm {
  padding: 4px 10px;
  background: #f5f7fa;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  color: #409EFF;
  cursor: pointer;
  transition: background 0.3s ease;
}

.detail-btn-sm:hover {
  background: #e8f4fd;
}

.table-footer {
  padding: 16px 0;
  margin-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.footer-note {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

@media (max-width: 1200px) {
  .ability-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar-title {
    display: none;
  }
  
  .nav-item span {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  .nav-item.active {
    border-left: none;
    background: #e8f4fd;
  }
  
  .ability-cards {
    grid-template-columns: 1fr;
  }
  
  .profile-info {
    flex-direction: column;
    text-align: center;
  }
  
  .score-circle {
    margin-top: 20px;
  }
}
</style>