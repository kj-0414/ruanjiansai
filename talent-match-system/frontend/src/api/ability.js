import request from '../services/request';

// 能力分析相关API
export const abilityApi = {
  // 创建能力图谱
  createAbilityMap: (user_id, ability_data) => {
    return request({
      url: '/ability/create',
      method: 'post',
      data: {
        user_id,
        ability_data: ability_data
      }
    });
  },

  // 获取能力树状图谱
  getAbilityTree: (user_id, resume_id = null) => {
    const url = resume_id 
      ? `/ability/tree/${user_id}?resume_id=${resume_id}`
      : `/ability/tree/${user_id}`;
    return request({
      url,
      method: 'get'
    });
  },

  // 获取能力雷达图数据
  getAbilityRadar: (user_id, resume_id = null) => {
    const url = resume_id 
      ? `/ability/radar/${user_id}?resume_id=${resume_id}`
      : `/ability/radar/${user_id}`;
    return request({
      url,
      method: 'get'
    });
  },

  // 获取文本分析
  getTextAnalysis: (user_id, resume_id = null) => {
    const url = resume_id 
      ? `/ability/text/${user_id}?resume_id=${resume_id}`
      : `/ability/text/${user_id}`;
    return request({
      url,
      method: 'get'
    });
  }
};