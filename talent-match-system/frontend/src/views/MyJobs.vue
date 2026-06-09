<template>
  <div class="my-jobs">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">我的岗位</h2>
        </div>
      </template>

      <div class="upload-section">
        <h3 class="section-title">上传岗位需求材料</h3>
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".pdf,.docx,.doc"
          multiple
          :file-list="uploadedFiles"
        >
          <el-button type="default">
            <el-icon><Upload /></el-icon>
            选择文件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持上传 PDF、Word 格式的文件，用于智能分析岗位需求
            </div>
          </template>
        </el-upload>

        <div class="form-actions">
          <button class="form-btn secondary" @click="analyzeFile" :disabled="isAnalyzing || uploadedFiles.length === 0">
            <span v-if="isAnalyzing">分析中...</span>
            <span v-else>AI智能分析</span>
          </button>
          <button class="form-btn primary" @click="generateAndSaveJob" :disabled="!extractedJobData || isSaving">
            <span v-if="isSaving">保存中...</span>
            <span v-else>保存岗位</span>
          </button>
        </div>

        <!-- AI分析结果预览 -->
        <div v-if="extractedJobData" class="form-container">
          <div class="form-section">
            <div class="form-section-title">AI分析结果预览</div>
          </div>
          
          <div class="form-grid">
            <div class="form-item">
              <label class="form-label">岗位名称</label>
              <input v-model="extractedJobData.jobName" class="form-input" placeholder="请输入岗位名称" />
            </div>
            <div class="form-item">
              <label class="form-label">薪资范围</label>
              <input v-model="extractedJobData.salary" class="form-input" placeholder="请输入薪资范围" />
            </div>
            <div class="form-item">
              <label class="form-label">工作地点</label>
              <input v-model="extractedJobData.location" class="form-input" placeholder="请输入工作地点" />
            </div>
            <div class="form-item">
              <label class="form-label">学历要求</label>
              <select v-model="extractedJobData.education" class="form-select" placeholder="请选择学历要求">
                <option value="不限">不限</option>
                <option value="初中">初中</option>
                <option value="高中">高中</option>
                <option value="大专">大专</option>
                <option value="本科">本科</option>
                <option value="硕士">硕士</option>
                <option value="博士">博士</option>
              </select>
            </div>
            <div class="form-item">
              <label class="form-label">经验要求</label>
              <input v-model="extractedJobData.experience" class="form-input" placeholder="请输入经验要求" />
            </div>
            <div class="form-item">
              <label class="form-label">公司名称</label>
              <input v-model="extractedJobData.companyName" class="form-input" placeholder="请输入公司名称" />
            </div>
            <div class="form-item">
              <label class="form-label">公司性质</label>
              <select v-model="extractedJobData.companyType" class="form-select">
                <option value="">请选择公司性质</option>
                <option value="国企">国企</option>
                <option value="外企">外企</option>
                <option value="民企">民企</option>
                <option value="上市公司">上市公司</option>
                <option value="创业公司">创业公司</option>
              </select>
            </div>
            <div class="form-item">
              <label class="form-label">公司规模</label>
              <select v-model="extractedJobData.companySize" class="form-select">
                <option value="">请选择公司规模</option>
                <option value="少于50人">少于50人</option>
                <option value="50-100人">50-100人</option>
                <option value="100-500人">100-500人</option>
                <option value="500-1000人">500-1000人</option>
                <option value="1000人以上">1000人以上</option>
              </select>
            </div>
            <div class="form-item">
              <label class="form-label">所属行业</label>
              <select v-model="extractedJobData.companyIndustry" class="form-select">
                <option value="">请选择行业</option>
                <option value="互联网/科技">互联网/科技</option>
                <option value="金融/投资">金融/投资</option>
                <option value="教育/培训">教育/培训</option>
                <option value="医疗/健康">医疗/健康</option>
                <option value="制造/工程">制造/工程</option>
                <option value="销售/市场">销售/市场</option>
                <option value="房地产">房地产</option>
                <option value="物流/运输">物流/运输</option>
                <option value="能源/化工">能源/化工</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-item full-width">
              <label class="form-label">公司简介</label>
              <textarea v-model="extractedJobData.companyIntro" class="form-textarea" rows="3" placeholder="请简要介绍公司的业务范围、发展历程、企业文化等"></textarea>
            </div>
            
            <div class="form-item full-width">
              <label class="form-label">公司标签</label>
              <div class="form-hint">选择公司特色标签（可多选）</div>
              <div class="form-tag-group">
                <label v-for="tag in companyTags" :key="tag.value" class="form-tag-option">
                  <input type="checkbox" v-model="extractedJobData.companyTags" :value="tag.value" />
                  <span>{{ tag.label }}</span>
                </label>
              </div>
            </div>
            
            <div class="form-item full-width">
              <label class="form-label">福利待遇</label>
              <div class="form-hint">选择提供的福利待遇（可多选）</div>
              <div class="form-tag-group">
                <label v-for="benefit in benefitsList" :key="benefit.value" class="form-tag-option">
                  <input type="checkbox" v-model="extractedJobData.selectedBenefits" :value="benefit.value" />
                  <span>{{ benefit.label }}</span>
                </label>
              </div>
            </div>
            
            <div class="form-item full-width">
              <label class="form-label">补充福利说明</label>
              <textarea v-model="extractedJobData.benefits" class="form-textarea" rows="2" placeholder="其他福利补充说明，如：年终奖发放规则、年假天数等"></textarea>
            </div>
            <div class="form-item">
              <label class="form-label">招聘人数</label>
              <input v-model="extractedJobData.recruitmentCount" type="number" class="form-input" placeholder="请输入招聘人数" />
            </div>
            <div class="form-item full-width">
              <label class="form-label">岗位描述</label>
              <textarea v-model="extractedJobData.description" class="form-textarea" rows="4" placeholder="请输入岗位描述"></textarea>
            </div>
            <div class="form-item full-width">
              <label class="form-label">岗位职责</label>
              <textarea v-model="extractedJobData.responsibilities" class="form-textarea" rows="3" placeholder="请输入岗位职责"></textarea>
            </div>
            <div class="form-item full-width">
              <label class="form-label">任职要求</label>
              <textarea v-model="extractedJobData.requirements" class="form-textarea" rows="3" placeholder="请输入任职要求"></textarea>
            </div>
            <div class="form-item full-width">
              <label class="form-label">所需技能</label>
              <div class="form-tags">
                <span v-for="(skill, index) in extractedJobData.skills" :key="index" class="form-tag">
                  {{ skill }}
                  <span class="remove-tag" @click="removeSkill(index)">×</span>
                </span>
              </div>
              <input 
                v-model="newSkill" 
                @keyup.enter="addSkill" 
                placeholder="按回车添加技能" 
                class="form-input"
              />
            </div>
            
            <div class="form-item full-width">
              <label class="form-label">学历惩罚设置</label>
              <div class="form-hint">设置惩罚百分比，100%表示完全惩罚，0%表示不惩罚</div>
              <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
                <div v-for="edu in educationLevels" :key="edu" style="display: flex; flex-direction: column; gap: 8px;">
                  <span style="font-size: 12px; color: var(--color-text-tertiary);">{{ edu }}</span>
                  <input 
                    type="range" 
                    v-model="extractedJobData.penaltyRules[edu]" 
                    min="0" 
                    max="100" 
                    style="width: 100%;"
                  />
                  <span style="font-size: 12px; color: var(--color-text-secondary);">惩罚{{ extractedJobData.penaltyRules[edu] }}%</span>
                </div>
              </div>
            </div>
            <div class="form-item full-width">
              <label class="form-label">技能要求（带优先级）</label>
              <div class="form-nested-list">
                <div v-for="(skill, index) in extractedJobData.skillRequirements" :key="index" class="form-nested-item">
                  <div class="nested-header">
                    <span class="item-title">技能要求 {{ index + 1 }}</span>
                    <span class="remove-item" @click="removeSkillRequirement(index)">×</span>
                  </div>
                  <div class="nested-content">
                    <input v-model="skill.name" class="form-input" placeholder="技能名称" />
                    <select v-model="skill.level" class="form-select">
                      <option value="初级">初级</option>
                      <option value="中级">中级</option>
                      <option value="高级">高级</option>
                    </select>
                    <div class="form-switch">
                      <input v-model="skill.required" type="checkbox" />
                      <span class="switch-label">必需</span>
                    </div>
                  </div>
                </div>
              </div>
              <button @click="addSkillRequirement" class="form-add-btn">+ 添加技能要求</button>
            </div>
            <div class="form-item full-width">
              <label class="form-label">证书要求</label>
              <div class="form-nested-list">
                <div v-for="(cert, index) in extractedJobData.certRequirements" :key="index" class="form-nested-item">
                  <div class="nested-header">
                    <span class="item-title">证书要求 {{ index + 1 }}</span>
                    <span class="remove-item" @click="removeCertRequirement(index)">×</span>
                  </div>
                  <div class="nested-content">
                    <input v-model="cert.name" class="form-input" placeholder="证书名称" />
                    <div class="form-switch">
                      <input v-model="cert.required" type="checkbox" />
                      <span class="switch-label">必需</span>
                    </div>
                  </div>
                </div>
              </div>
              <button @click="addCertRequirement" class="form-add-btn">+ 添加证书要求</button>
            </div>
            <div class="form-item full-width">
              <label class="form-label">项目经验要求</label>
              <div class="form-nested-list">
                <div v-for="(project, index) in extractedJobData.projectRequirements" :key="index" class="form-nested-item">
                  <div class="nested-header">
                    <span class="item-title">项目要求 {{ index + 1 }}</span>
                    <span class="remove-item" @click="removeProjectRequirement(index)">×</span>
                  </div>
                  <div class="nested-content">
                    <input v-model="project.domain" class="form-input" placeholder="领域" />
                    <input v-model="project.min_years" type="number" class="form-input" placeholder="最少年限" />
                    <input v-model="project.tech_stack" class="form-input" placeholder="技术栈（逗号分隔）" />
                  </div>
                </div>
              </div>
              <button @click="addProjectRequirement" class="form-add-btn">+ 添加项目要求</button>
            </div>
            
          </div>
        </div>
      </div>

      <div class="job-list" v-if="jobs.length > 0">
        <h3 class="section-title">已保存的岗位</h3>
        <el-table :data="jobs" style="width: 100%">
          <el-table-column prop="job_name" label="岗位名称" width="200" />
          <el-table-column prop="salary" label="薪资" width="100" />
          <el-table-column prop="location" label="地点" width="100" />
          <el-table-column prop="education_requirement" label="学历要求" width="120" />
          
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="viewJob(scope.row)">查看</el-button>
              <el-button size="small" @click="editJob(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteJob(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else-if="uploadedFiles.length === 0 && !extractedJobData" class="empty-state">
        <el-empty description="请上传岗位需求材料以生成岗位信息" />
      </div>

      <!-- 岗位查看/编辑对话框 -->
      <el-dialog
        v-model="jobPreviewDialog"
        :title="isEditing ? '编辑岗位' : '查看岗位'"
        width="800px"
        fullscreen
      >
        <div class="job-preview" v-if="!isEditing">
          <div class="job-header">
            <h2>{{ currentJob?.job_name }}</h2>
            <p class="job-meta">
              创建时间：{{ currentJob?.created_at }} | 薪资：{{ currentJob?.salary }} | 地点：{{ currentJob?.location }}
            </p>
          </div>
          
          <div class="job-content">
            <div class="job-section">
              <h3>岗位描述</h3>
              <div class="job-description">
                {{ currentJob?.job_desc || '暂无岗位描述' }}
              </div>
            </div>

            <div class="job-section">
              <h3>岗位职责</h3>
              <div class="job-responsibilities">
                <ul v-if="currentJob?.responsibilities">
                  <li v-for="(item, index) in parseJson(currentJob.responsibilities)" :key="index">{{ item }}</li>
                </ul>
                <div v-else class="empty-content">暂无岗位职责信息</div>
              </div>
            </div>

            <div class="job-section">
              <h3>任职要求</h3>
              <div class="job-requirements">
                <ul v-if="currentJob?.requirements">
                  <li v-for="(item, index) in parseJson(currentJob.requirements)" :key="index">{{ item }}</li>
                </ul>
                <div v-else class="empty-content">暂无任职要求信息</div>
              </div>
            </div>

            <div class="job-section">
              <h3>岗位要求</h3>
              <div class="job-requirement-grid">
                <div class="requirement-item">
                  <span class="requirement-label">学历要求</span>
                  <span class="requirement-value">{{ currentJob?.education_requirement || '不限' }}</span>
                </div>
                <div class="requirement-item">
                  <span class="requirement-label">工作经验</span>
                  <span class="requirement-value">{{ currentJob?.experience_requirement || '不限' }}</span>
                </div>
                <div class="requirement-item">
                  <span class="requirement-label">招聘人数</span>
                  <span class="requirement-value">{{ currentJob?.recruitment_count || '1' }}人</span>
                </div>
                <div class="requirement-item">
                  <span class="requirement-label">工作地点</span>
                  <span class="requirement-value">{{ currentJob?.location || '未指定' }}</span>
                </div>
                <div class="requirement-item">
                  <span class="requirement-label">薪资待遇</span>
                  <span class="requirement-value">{{ currentJob?.salary || '面议' }}</span>
                </div>
                <div class="requirement-item">
                  <span class="requirement-label">工作类型</span>
                  <span class="requirement-value">{{ currentJob?.job_type || '全职' }}</span>
                </div>
              </div>
            </div>

            <div class="job-section">
              <h3>所需技能</h3>
              <div v-if="currentJob?.skills" class="job-skills">
                <span v-for="(skill, index) in parseJson(currentJob.skills)" :key="index" class="skill-tag">
                  {{ skill }}
                </span>
              </div>
              <div v-else class="empty-content">暂无技能要求信息</div>
            </div>

            <div class="job-section">
              <h3>福利待遇</h3>
              <div class="job-benefits">
                {{ currentJob?.benefits || '暂无福利待遇信息' }}
              </div>
            </div>

            <div class="job-section">
              <h3>公司信息</h3>
              <div class="company-info-grid">
                <div class="company-item">
                  <span class="company-label">公司名称</span>
                  <span class="company-value">{{ currentJob?.company_name || '未填写' }}</span>
                </div>
                <div class="company-item">
                  <span class="company-label">公司性质</span>
                  <span class="company-value">{{ currentJob?.company_type || '未填写' }}</span>
                </div>
                <div class="company-item">
                  <span class="company-label">公司规模</span>
                  <span class="company-value">{{ currentJob?.company_size || '未填写' }}</span>
                </div>
                <div class="company-item">
                  <span class="company-label">所属行业</span>
                  <span class="company-value">{{ currentJob?.company_industry || '未填写' }}</span>
                </div>
              </div>
              <div v-if="currentJob?.company_intro" class="company-intro">
                <span class="company-label">公司简介</span>
                <p>{{ currentJob?.company_intro }}</p>
              </div>
              <div v-if="currentJob?.company_tags" class="company-tags">
                <span class="company-label">公司标签</span>
                <div class="tags-list">
                  <span v-for="(tag, index) in parseJson(currentJob.company_tags)" :key="index" class="tag-item">{{ tag }}</span>
                </div>
              </div>
            </div>

            <div class="job-section">
              <h3>福利待遇明细</h3>
              <div v-if="currentJob?.selected_benefits" class="benefits-detail">
                <span v-for="(benefit, index) in parseJson(currentJob.selected_benefits)" :key="index" class="benefit-item">{{ benefit }}</span>
              </div>
              <div v-else class="empty-content">暂无福利待遇明细信息</div>
            </div>
          </div>
        </div>

        <!-- 编辑模式表单 -->
        <div class="job-edit" v-else>
          <div class="edit-form">
            <div class="form-row">
              <div class="form-item">
                <label>岗位名称</label>
                <input v-model="editJobData.jobName" class="form-input" />
              </div>
              <div class="form-item">
                <label>薪资范围</label>
                <input v-model="editJobData.salary" class="form-input" />
              </div>
              <div class="form-item">
                <label>工作地点</label>
                <input v-model="editJobData.location" class="form-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-item">
                <label>学历要求</label>
                <el-select v-model="editJobData.education" class="form-select">
                  <el-option label="不限" value="不限" />
                  <el-option label="初中" value="初中" />
                  <el-option label="高中" value="高中" />
                  <el-option label="大专" value="大专" />
                  <el-option label="本科" value="本科" />
                  <el-option label="硕士" value="硕士" />
                  <el-option label="博士" value="博士" />
                </el-select>
              </div>
              <div class="form-item">
                <label>工作经验</label>
                <input v-model="editJobData.experience" class="form-input" />
              </div>
              <div class="form-item">
                <label>招聘人数</label>
                <input v-model="editJobData.recruitmentCount" type="number" class="form-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-item">
                <label>工作类型</label>
                <el-select v-model="editJobData.jobType" class="form-select">
                  <el-option label="全职" value="全职" />
                  <el-option label="兼职" value="兼职" />
                  <el-option label="实习" value="实习" />
                </el-select>
              </div>
              <div class="form-item">
                <label>所属部门</label>
                <input v-model="editJobData.department" class="form-input" />
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>岗位描述</label>
                <textarea v-model="editJobData.description" class="form-textarea" rows="4"></textarea>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>岗位职责</label>
                <textarea v-model="editJobData.responsibilities" class="form-textarea" rows="4" placeholder="每条职责一行"></textarea>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>任职要求</label>
                <textarea v-model="editJobData.requirements" class="form-textarea" rows="4" placeholder="每条要求一行"></textarea>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>所需技能</label>
                <div class="skills-tags">
                  <span v-for="(skill, index) in editJobData.skills" :key="index" class="skill-tag">
                    {{ skill }}
                    <span class="remove-skill" @click="removeEditSkill(index)">×</span>
                  </span>
                </div>
                <input 
                  v-model="editNewSkill" 
                  @keyup.enter="addEditSkill" 
                  placeholder="按回车添加技能" 
                  class="skill-input"
                />
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>福利待遇</label>
                <textarea v-model="editJobData.benefits" class="form-textarea" rows="2"></textarea>
              </div>
            </div>

            <div class="form-row">
              <div class="form-item">
                <label>公司名称</label>
                <input v-model="editJobData.companyName" class="form-input" />
              </div>
              <div class="form-item">
                <label>公司性质</label>
                <select v-model="editJobData.companyType" class="form-select">
                  <option value="">请选择公司性质</option>
                  <option value="国企">国企</option>
                  <option value="外企">外企</option>
                  <option value="民企">民企</option>
                  <option value="上市公司">上市公司</option>
                  <option value="创业公司">创业公司</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-item">
                <label>公司规模</label>
                <select v-model="editJobData.companySize" class="form-select">
                  <option value="">请选择公司规模</option>
                  <option value="少于50人">少于50人</option>
                  <option value="50-100人">50-100人</option>
                  <option value="100-500人">100-500人</option>
                  <option value="500-1000人">500-1000人</option>
                  <option value="1000人以上">1000人以上</option>
                </select>
              </div>
              <div class="form-item">
                <label>所属行业</label>
                <select v-model="editJobData.companyIndustry" class="form-select">
                  <option value="">请选择行业</option>
                  <option value="互联网/科技">互联网/科技</option>
                  <option value="金融/投资">金融/投资</option>
                  <option value="教育/培训">教育/培训</option>
                  <option value="医疗/健康">医疗/健康</option>
                  <option value="制造/工程">制造/工程</option>
                  <option value="销售/市场">销售/市场</option>
                  <option value="房地产">房地产</option>
                  <option value="物流/运输">物流/运输</option>
                  <option value="能源/化工">能源/化工</option>
                  <option value="其他">其他</option>
                </select>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>公司简介</label>
                <textarea v-model="editJobData.companyIntro" class="form-textarea" rows="3"></textarea>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>公司标签</label>
                <div class="form-hint">选择公司特色标签（可多选）</div>
                <el-checkbox-group v-model="editJobData.companyTags" class="checkbox-group">
                  <el-checkbox v-for="tag in companyTags" :key="tag.value" :label="tag.value" />
                </el-checkbox-group>
              </div>
            </div>

            <div class="form-row full-width">
              <div class="form-item">
                <label>福利待遇明细</label>
                <div class="form-hint">选择提供的福利待遇（可多选）</div>
                <el-checkbox-group v-model="editJobData.selectedBenefits" class="checkbox-group">
                  <el-checkbox v-for="benefit in benefitsList" :key="benefit.value" :label="benefit.value" />
                </el-checkbox-group>
              </div>
            </div>
          </div>
        </div>

        <template #footer>
          <span class="dialog-footer">
            <el-button @click="jobPreviewDialog = false">关闭</el-button>
            <el-button v-if="isEditing" type="primary" @click="saveEditJob" :loading="isSaving">
              保存修改
            </el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document, Search } from '@element-plus/icons-vue'
import service from '../services/request'

// 学历级别列表（只保留到大专）
const educationLevels = ['博士', '硕士', '本科', '大专']

// 初始化学历惩罚规则
const initPenaltyRules = () => {
  const rules = {}
  educationLevels.forEach(edu => {
    rules[edu] = 100
  })
  return rules
}

// 上传的材料文件列表
const uploadedFiles = ref([])
// 保存的岗位列表
const jobs = ref([])
// 岗位预览对话框
const jobPreviewDialog = ref(false)
// 当前查看的岗位
const currentJob = ref(null)
// 是否正在分析
const isAnalyzing = ref(false)
// 是否正在保存
const isSaving = ref(false)
// 是否正在编辑
const isEditing = ref(false)
// AI分析提取的数据
const extractedJobData = ref(null)
// 新技能输入
const newSkill = ref('')

// 公司标签选项
const companyTags = ref([
  { label: '扁平化管理', value: '扁平化管理' },
  { label: '弹性工作', value: '弹性工作' },
  { label: '年终奖', value: '年终奖' },
  { label: '五险一金', value: '五险一金' },
  { label: '带薪年假', value: '带薪年假' },
  { label: '定期体检', value: '定期体检' },
  { label: '员工旅游', value: '员工旅游' },
  { label: '餐补', value: '餐补' },
  { label: '交通补助', value: '交通补助' },
  { label: '住房补贴', value: '住房补贴' },
  { label: '加班补助', value: '加班补助' },
  { label: '股票期权', value: '股票期权' },
  { label: '导师制', value: '导师制' },
  { label: '培训机会', value: '培训机会' },
  { label: '晋升空间', value: '晋升空间' },
  { label: '团建活动', value: '团建活动' }
])

// 福利待遇选项
const benefitsList = ref([
  { label: '养老保险', value: '养老保险' },
  { label: '医疗保险', value: '医疗保险' },
  { label: '失业保险', value: '失业保险' },
  { label: '工伤保险', value: '工伤保险' },
  { label: '生育保险', value: '生育保险' },
  { label: '住房公积金', value: '住房公积金' },
  { label: '补充医疗保险', value: '补充医疗保险' },
  { label: '年终奖', value: '年终奖' },
  { label: '绩效奖金', value: '绩效奖金' },
  { label: '全勤奖', value: '全勤奖' },
  { label: '带薪年假', value: '带薪年假' },
  { label: '病假', value: '病假' },
  { label: '婚假', value: '婚假' },
  { label: '产假', value: '产假' },
  { label: '陪产假', value: '陪产假' },
  { label: '丧假', value: '丧假' },
  { label: '带薪培训', value: '带薪培训' },
  { label: '餐补', value: '餐补' },
  { label: '交通补助', value: '交通补助' },
  { label: '住房补贴', value: '住房补贴' },
  { label: '通讯补贴', value: '通讯补贴' },
  { label: '加班补助', value: '加班补助' },
  { label: '定期体检', value: '定期体检' },
  { label: '员工旅游', value: '员工旅游' },
  { label: '团建活动', value: '团建活动' },
  { label: '节日福利', value: '节日福利' },
  { label: '生日福利', value: '生日福利' },
  { label: '年终聚餐', value: '年终聚餐' },
  { label: '股票期权', value: '股票期权' },
  { label: '项目奖金', value: '项目奖金' }
])

// 编辑数据
const editJobData = ref({
  jobName: '',
  salary: '',
  location: '',
  education: '不限',
  experience: '',
  recruitmentCount: 1,
  jobType: '全职',
  department: '',
  description: '',
  responsibilities: '',
  requirements: '',
  skills: [],
  benefits: '',
  companyName: '',
  companyType: '',
  companySize: '',
  companyIndustry: '',
  companyIntro: '',
  companyTags: [],
  selectedBenefits: []
})
// 编辑时新技能输入
const editNewSkill = ref('')

// 添加技能要求
const addSkillRequirement = () => {
  if (!extractedJobData.value.skillRequirements) {
    extractedJobData.value.skillRequirements = []
  }
  extractedJobData.value.skillRequirements.push({
    name: '',
    level: '中级',
    required: false
  })
}

// 移除技能要求
const removeSkillRequirement = (index) => {
  extractedJobData.value.skillRequirements.splice(index, 1)
}

// 添加证书要求
const addCertRequirement = () => {
  if (!extractedJobData.value.certRequirements) {
    extractedJobData.value.certRequirements = []
  }
  extractedJobData.value.certRequirements.push({
    name: '',
    required: false
  })
}

// 移除证书要求
const removeCertRequirement = (index) => {
  extractedJobData.value.certRequirements.splice(index, 1)
}

// 添加项目要求
const addProjectRequirement = () => {
  if (!extractedJobData.value.projectRequirements) {
    extractedJobData.value.projectRequirements = []
  }
  extractedJobData.value.projectRequirements.push({
    domain: '',
    min_years: 1,
    tech_stack: ''
  })
}

// 移除项目要求
const removeProjectRequirement = (index) => {
  extractedJobData.value.projectRequirements.splice(index, 1)
}

// 从后端获取岗位列表
const fetchJobs = async () => {
  try {
    const response = await service.get('/job')
    if (response) {
      jobs.value = response
    }
  } catch (error) {
    console.error('获取岗位列表失败:', error)
    ElMessage.error('获取岗位列表失败')
  }
}

onMounted(() => {
  fetchJobs()
})

// 处理文件上传
const handleFileChange = (file) => {
  uploadedFiles.value.push(file)
  ElMessage.success('材料上传成功')
  extractedJobData.value = null
}

// 处理文件移除
const handleFileRemove = (file) => {
  const index = uploadedFiles.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    uploadedFiles.value.splice(index, 1)
    ElMessage.success('材料移除成功')
    if (uploadedFiles.value.length === 0) {
      extractedJobData.value = null
    }
  }
}

// AI分析文件
const analyzeFile = async () => {
  if (uploadedFiles.value.length === 0) {
    ElMessage.error('请先上传岗位需求材料')
    return
  }

  isAnalyzing.value = true
  ElMessage.info('正在进行AI智能分析...')

  try {
    const formData = new FormData()
    uploadedFiles.value.forEach((file, index) => {
      formData.append('files', file.raw, file.name)
    })

    const response = await service.post('/job/extract-job', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    console.log('AI分析结果:', response)

    // 初始化提取的数据
    extractedJobData.value = {
      jobName: response.jobName || uploadedFiles.value[0].name.replace(/\.[^/.]+$/, ''),
      salary: response.salary || '',
      location: response.location || '',
      education: response.education || '不限',
      experience: response.experience || '',
      recruitmentCount: response.recruitmentCount || 1,
      description: response.description || '',
      responsibilities: response.responsibilities || '',
      requirements: response.requirements || '',
      skills: Array.isArray(response.skills) ? response.skills : [],
      benefits: '',
      penaltyRules: initPenaltyRules(),
      // 新增字段 - 从AI解析结果中自动提取
      skillRequirements: Array.isArray(response.skillRequirements) ? response.skillRequirements.map(s => ({
        name: s.name || '',
        level: s.level || '中级',
        required: s.required || false
      })) : [],
      certRequirements: Array.isArray(response.certRequirements) ? response.certRequirements.map(c => ({
        name: c.name || '',
        required: c.required || false
      })) : [],
      projectRequirements: Array.isArray(response.projectRequirements) ? response.projectRequirements.map(p => ({
        domain: p.domain || '',
        min_years: p.min_years || 1,
        tech_stack: p.tech_stack || ''
      })) : [],
      industry: response.industry || '',
      min_experience_years: response.minExperienceYears || 0,
      max_experience_years: response.maxExperienceYears || 0,
      education_level: response.education || '不限',
      tech_tags: Array.isArray(response.techTags) ? response.techTags : []
    }

    ElMessage.success('AI分析完成，请确认并编辑信息')
  } catch (error) {
    ElMessage.error('AI分析失败，请重试')
    console.error('AI分析失败:', error)
    console.error('错误详情:', error.response ? error.response.data : error.message)
  } finally {
    isAnalyzing.value = false
  }
}

// 添加技能
const addSkill = () => {
  if (newSkill.value.trim() && extractedJobData.value) {
    if (!extractedJobData.value.skills.includes(newSkill.value.trim())) {
      extractedJobData.value.skills.push(newSkill.value.trim())
    }
    newSkill.value = ''
  }
}

// 移除技能
const removeSkill = (index) => {
  if (extractedJobData.value) {
    extractedJobData.value.skills.splice(index, 1)
  }
}

// 生成并保存岗位
const generateAndSaveJob = async () => {
  if (!extractedJobData.value) {
    ElMessage.error('请先进行AI分析')
    return
  }

  isSaving.value = true
  ElMessage.info('正在保存岗位信息...')

  try {
    // 技能要求转换
    const skillRequirements = (extractedJobData.value.skillRequirements || []).map(s => ({
      skill_name: s.name,
      required: s.required,
      level: s.level
    }))
    
    // 证书要求转换
    const certRequirements = (extractedJobData.value.certRequirements || []).map(c => ({
      name: c.name,
      required: c.required
    }))
    
    // 项目要求转换
    const projectRequirements = (extractedJobData.value.projectRequirements || []).map(p => ({
      domain: p.domain,
      min_years: parseInt(p.min_years) || 1,
      tech_stack: p.tech_stack ? p.tech_stack.split(',').map(s => s.trim()) : []
    }))
    
    const jobData = {
      job_name: extractedJobData.value.jobName,
      job_desc: extractedJobData.value.description,
      salary: extractedJobData.value.salary,
      location: extractedJobData.value.location,
      education_requirement: extractedJobData.value.education,
      experience_requirement: extractedJobData.value.experience,
      recruitment_count: extractedJobData.value.recruitmentCount.toString(),
      responsibilities: JSON.stringify(extractedJobData.value.responsibilities.split('\n').filter(item => item.trim())),
      requirements: JSON.stringify(extractedJobData.value.requirements.split('\n').filter(item => item.trim())),
      skills: JSON.stringify(extractedJobData.value.skills),
      benefits: extractedJobData.value.benefits || '',
      job_type: '全职',
      department: '',
      work_hours: '',
      education_penalty_rules: JSON.stringify(extractedJobData.value.penaltyRules || initPenaltyRules()),
      // 新增字段
      skills_requirement: JSON.stringify(skillRequirements),
      certificate_requirements: JSON.stringify(certRequirements),
      project_requirements: JSON.stringify(projectRequirements),
      education_level: extractedJobData.value.education_level || extractedJobData.value.education,
      min_experience_years: parseInt(extractedJobData.value.min_experience_years) || 0,
      max_experience_years: parseInt(extractedJobData.value.max_experience_years) || 0,
      industry: extractedJobData.value.companyIndustry || '',
      tech_tags: JSON.stringify(extractedJobData.value.tech_tags || []),
      // 公司信息字段
      company_name: extractedJobData.value.companyName || '',
      company_type: extractedJobData.value.companyType || '',
      company_size: extractedJobData.value.companySize || '',
      company_industry: extractedJobData.value.companyIndustry || '',
      company_intro: extractedJobData.value.companyIntro || '',
      company_tags: JSON.stringify(extractedJobData.value.companyTags || []),
      selected_benefits: JSON.stringify(extractedJobData.value.selectedBenefits || [])
    }

    await service.post('/job', jobData)

    await fetchJobs()

    uploadedFiles.value = []
    extractedJobData.value = null

    ElMessage.success('岗位保存成功')
  } catch (error) {
    ElMessage.error('保存岗位失败，请重试')
    console.error('保存岗位失败:', error)
    console.error('错误详情:', error.response ? error.response.data : error.message)
  } finally {
    isSaving.value = false
  }
}

// 查看岗位
const viewJob = (job) => {
  isEditing.value = false
  currentJob.value = job
  jobPreviewDialog.value = true
}

// 解析JSON数据
const parseJson = (jsonStr) => {
  try {
    if (!jsonStr) return []
    return JSON.parse(jsonStr)
  } catch {
    return []
  }
}

// 编辑岗位
const editJob = async (job) => {
  isEditing.value = true
  currentJob.value = job
  
  // 初始化编辑表单数据
  editJobData.value = {
    jobName: job.job_name || '',
    salary: job.salary || '',
    location: job.location || '',
    education: job.education_requirement || '不限',
    experience: job.experience_requirement || '',
    recruitmentCount: parseInt(job.recruitment_count) || 1,
    jobType: job.job_type || '全职',
    department: job.department || '',
    description: job.job_desc || '',
    responsibilities: typeof job.responsibilities === 'string' ? parseJson(job.responsibilities).join('\n') : '',
    requirements: typeof job.requirements === 'string' ? parseJson(job.requirements).join('\n') : '',
    skills: typeof job.skills === 'string' ? parseJson(job.skills) : [],
    benefits: job.benefits || '',
    // 公司信息
    companyName: job.company_name || '',
    companyType: job.company_type || '',
    companySize: job.company_size || '',
    companyIndustry: job.company_industry || '',
    companyIntro: job.company_intro || '',
    companyTags: typeof job.company_tags === 'string' ? parseJson(job.company_tags) : [],
    selectedBenefits: typeof job.selected_benefits === 'string' ? parseJson(job.selected_benefits) : []
  }
  
  jobPreviewDialog.value = true
}

// 添加编辑技能
const addEditSkill = () => {
  if (editNewSkill.value.trim()) {
    if (!editJobData.value.skills.includes(editNewSkill.value.trim())) {
      editJobData.value.skills.push(editNewSkill.value.trim())
    }
    editNewSkill.value = ''
  }
}

// 移除编辑技能
const removeEditSkill = (index) => {
  editJobData.value.skills.splice(index, 1)
}

// 保存编辑岗位
const saveEditJob = async () => {
  isSaving.value = true
  ElMessage.info('正在保存修改...')
  
  try {
    const jobData = {
      job_name: editJobData.value.jobName,
      job_desc: editJobData.value.description,
      salary: editJobData.value.salary,
      location: editJobData.value.location,
      education_requirement: editJobData.value.education,
      experience_requirement: editJobData.value.experience,
      recruitment_count: editJobData.value.recruitmentCount.toString(),
      job_type: editJobData.value.jobType,
      department: editJobData.value.department,
      benefits: editJobData.value.benefits,
      responsibilities: JSON.stringify(editJobData.value.responsibilities.split('\n').filter(item => item.trim())),
      requirements: JSON.stringify(editJobData.value.requirements.split('\n').filter(item => item.trim())),
      skills: JSON.stringify(editJobData.value.skills),
      work_hours: '',
      // 添加公司信息字段
      company_name: editJobData.value.companyName || '',
      company_type: editJobData.value.companyType || '',
      company_size: editJobData.value.companySize || '',
      company_industry: editJobData.value.companyIndustry || '',
      company_intro: editJobData.value.companyIntro || '',
      company_tags: JSON.stringify(editJobData.value.companyTags || []),
      selected_benefits: JSON.stringify(editJobData.value.selectedBenefits || [])
    }
    
    await service.put(`/job/${currentJob.value.id}`, jobData)
    
    await fetchJobs()
    
    jobPreviewDialog.value = false
    isEditing.value = false
    
    ElMessage.success('岗位修改成功')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
    console.error('保存岗位失败:', error)
  } finally {
    isSaving.value = false
  }
}

// 删除岗位
const deleteJob = async (job) => {
  try {
    await service.delete(`/job/${job.id}`)
    await fetchJobs()
    ElMessage.success('岗位删除成功')
  } catch (error) {
    console.error('删除岗位失败:', error)
    ElMessage.error('删除岗位失败')
  }
}
</script>

<style scoped>
.my-jobs {
  padding: 20px;
}

.page-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.upload-section {
  margin: 20px 0;
}

.action-section {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 20px 0 10px;
}

.empty-state {
  margin: 40px 0;
  text-align: center;
}

/* AI分析结果预览样式 */
.analysis-preview {
  margin-top: 20px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.analysis-item {
  display: flex;
  flex-direction: column;
}

.analysis-item.full-width {
  grid-column: span 3;
}

.analysis-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 5px;
}

.analysis-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

.analysis-textarea {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  resize: none;
  background-color: white;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.skill-tag {
  background-color: #ecf5ff;
  color: #409EFF;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  position: relative;
}

.remove-skill {
  margin-left: 6px;
  cursor: pointer;
  color: #909399;
}

.remove-skill:hover {
  color: #f56c6c;
}

.skill-input {
  padding: 6px 12px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  background-color: white;
}

/* 新增字段样式 */
.skill-requirements-list,
.cert-requirements-list,
.project-requirements-list {
  margin-bottom: 8px;
}

.skill-requirement-item,
.cert-requirement-item,
.project-requirement-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  position: relative;
  align-items: center;
}

.project-requirement-item {
  flex-wrap: wrap;
}

.skill-requirement-item input,
.cert-requirement-item input,
.project-requirement-item input {
  flex: 1;
  min-width: 120px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #606266;
}

.remove-skill-req,
.remove-cert-req,
.remove-project-req {
  position: absolute;
  top: 5px;
  right: 10px;
  cursor: pointer;
  color: #909399;
  font-size: 18px;
}

.remove-skill-req:hover,
.remove-cert-req:hover,
.remove-project-req:hover {
  color: #f56c6c;
}

.add-btn {
  padding: 6px 12px;
  border: 1px dashed #409EFF;
  border-radius: 4px;
  background-color: #ecf5ff;
  color: #409EFF;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn:hover {
  background-color: #409EFF;
  color: white;
  border-style: solid;
}

/* 岗位预览样式 */
.job-preview {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
  background-color: white;
  min-height: 100vh;
}

.job-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.job-header h2 {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.job-meta {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.job-content {
  margin-top: 30px;
}

.job-section {
  margin-bottom: 30px;
}

.job-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.job-description,
.job-benefits {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  text-align: justify;
}

.job-responsibilities,
.job-requirements {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
}

.job-responsibilities ul,
.job-requirements ul {
  padding-left: 20px;
  margin: 0;
}

.job-responsibilities li,
.job-requirements li {
  margin-bottom: 8px;
  position: relative;
  padding-left: 10px;
}

.job-responsibilities li::before,
.job-requirements li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #409EFF;
}

.job-requirement-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.requirement-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background-color: #fafafa;
  border-radius: 8px;
}

.requirement-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.requirement-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.job-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.empty-content {
  font-size: 14px;
  color: #909399;
  font-style: italic;
}

/* 编辑表单样式 */
.job-edit {
  padding: 40px;
  max-width: 900px;
  margin: 0 auto;
  background-color: #fafafa;
  min-height: 100vh;
}

.edit-form {
  background-color: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.form-row.full-width {
  grid-template-columns: 1fr;
}

.form-item {
  display: flex;
  flex-direction: column;
}

.form-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background-color: white;
}

.form-input:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-select {
  padding: 10px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
  background-color: white;
}

.form-select:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-textarea {
  padding: 12px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  transition: all 0.2s ease;
  background-color: white;
}

.form-textarea:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.skill-input {
  padding: 10px 14px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  background-color: #fafafa;
  width: 100%;
  transition: all 0.2s ease;
}

.skill-input:focus {
  outline: none;
  border-color: #409EFF;
  border-style: solid;
  background-color: white;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 学历惩罚设置样式 */
.penalty-section {
  margin-top: 10px;
}

.penalty-config {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
}

.penalty-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.penalty-item:last-child {
  border-bottom: none;
}

.penalty-label {
  font-size: 14px;
  color: #606266;
  width: 60px;
  flex-shrink: 0;
}

.penalty-slider-wrap {
  display: flex;
  align-items: center;
  flex: 1;
  margin-left: 20px;
}

.penalty-slider {
  flex: 1;
  height: 6px;
  background-color: #e4e7ed;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.penalty-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background-color: #409EFF;
  border-radius: 50%;
  cursor: pointer;
}

.penalty-value {
  margin-left: 15px;
  font-size: 14px;
  font-weight: 500;
  color: #409EFF;
  min-width: 50px;
  text-align: right;
}
</style>
