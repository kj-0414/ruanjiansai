import service from '../services/request';

export const jobAbilityApi = {
  // 创建岗位能力图谱
  createJobAbilityMap: (jobId) => service.post('/job/ability/create', {
    job_id: jobId
  }),
  
  // 获取岗位能力树
  getJobAbilityTree: (jobId) => service.get(`/job/ability/tree/${jobId}`),
  
  // 更新岗位能力节点
  updateJobAbilityNode: (nodeId, nodeData) => service.put(`/job/ability/update/${nodeId}`, nodeData),
  
  // 删除岗位能力图谱
  deleteJobAbilityMap: (jobId) => service.delete(`/job/ability/delete/${jobId}`)
};

export default jobAbilityApi;