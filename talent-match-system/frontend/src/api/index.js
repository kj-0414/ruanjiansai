import service from '../services/request';

export const authAPI = {
  login: (data) => service.post('/user/login', {
    phone: data.phone,
    password: data.password,
    role: data.role
  }),
  logout: () => service.post('/user/logout')
};

// 用户相关API
export const userAPI = {
  // 发送验证码
  sendCode: (data) => service.post('/user/send-code', {
    phone: data.phone
  }),
  
  // 注册
  register: (data) => service.post('/user/register', {
    phone: data.phone,
    nickname: data.nickname,
    code: data.code,
    password: data.password,
    role: data.role
  }),

  getInfo: () => service.get('/user/me')
};

// 岗位相关API
export const jobAPI = {
  createJob: (data) => service.post('/job', {
    job_name: data.job_name,
    job_desc: data.job_desc,
    salary: data.salary,
    location: data.location,
    work_hours: data.work_hours,
    education_requirement: data.education_requirement,
    experience_requirement: data.experience_requirement,
    recruitment_count: data.recruitment_count,
    department: data.department,
    job_type: data.job_type,
    benefits: data.benefits
  }),
  getJobs: () => service.get('/job'),
  getJobById: (jobId) => service.get(`/job/${jobId}`),
  updateJob: (job_id, data) => service.put(`/job/${job_id}`, {
    job_name: data.job_name,
    job_desc: data.job_desc,
    salary: data.salary,
    location: data.location,
    work_hours: data.work_hours,
    education_requirement: data.education_requirement,
    experience_requirement: data.experience_requirement,
    recruitment_count: data.recruitment_count,
    department: data.department,
    job_type: data.job_type,
    benefits: data.benefits
  }),
  deleteJob: (job_id) => service.delete(`/job/${job_id}`),
  uploadJobRequirement: (formData, jobName) => service.post(`/job/upload?job_name=${encodeURIComponent(jobName)}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
};

// 简历相关API
export const resumeAPI = {
  uploadResume: (formData) => service.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  getResumes: () => service.get('/resume'),
  getResumeById: (resumeId) => service.get(`/resume/${resumeId}`)
};

// 匹配相关API
export const matchAPI = {
  matchResumeJob: (data) => service.post('/match', data),
  getMatchRecords: () => service.get('/match/records'),
  getMatchRecord: (matchId) => service.get(`/match/${matchId}`)
};

export default service;
