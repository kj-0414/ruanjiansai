import service from '../services/request';

export const adminAPI = {
  getUsers: (offset = 0, limit = 10) => service.get(`/admin/users?offset=${offset}&limit=${limit}`),
  
  getUser: (userId) => service.get(`/admin/users/${userId}`),
  
  updateUserRoles: (userId, roles) => service.put(`/admin/users/${userId}/roles`, {
    roles: roles
  }),
  
  deleteUser: (userId) => service.delete(`/admin/users/${userId}`),
  
  getStats: () => service.get('/admin/stats'),
  
  promoteToAdmin: (userId) => service.post(`/admin/users/${userId}/promote`)
};

export default adminAPI;