import request from '../services/request'

export const messageApi = {
  createConversation: (jobSeekerId, companyId, jobId, resumeId) => {
    return request.post('/message/conversations', null, {
      params: {
        job_seeker_id: jobSeekerId,
        company_id: companyId,
        job_id: jobId,
        resume_id: resumeId
      }
    })
  },

  getUserConversations: (user_role, page = 1, page_size = 20) => {
    return request.get('/message/conversations', {
      params: {
        user_role,
        page,
        page_size
      }
    })
  },

  getConversation: (conversationId) => {
    return request.get(`/message/conversations/${conversationId}`)
  },

  sendMessage: (conversationId, receiverId, content, userRole = 'job_seeker') => {
    return request.post(`/message/conversations/${conversationId}/messages`, null, {
      params: {
        receiver_id: receiverId,
        content,
        user_role: userRole
      }
    })
  },

  getPendingConversations: () => {
    return request.get('/message/conversations/pending')
  },

  getPendingConversationsForJobSeeker: () => {
    return request.get('/message/conversations/pending/job-seeker')
  },

  activateConversation: (conversationId) => {
    return request.post(`/message/conversations/${conversationId}/activate`)
  },

  activateConversationByJobSeeker: (conversationId) => {
    return request.post(`/message/conversations/${conversationId}/activate-by-job-seeker`)
  },

  getConversationMessages: (conversationId, page = 1, pageSize = 20) => {
    return request.get(`/message/conversations/${conversationId}/messages`, {
      params: {
        page,
        page_size: pageSize
      }
    })
  },

  markConversationRead: (conversationId) => {
    return request.put(`/message/conversations/${conversationId}/read`)
  },

  closeConversation: (conversationId) => {
    return request.put(`/message/conversations/${conversationId}/close`)
  },

  getUnreadCount: (userRole) => {
    return request.get('/message/unread-count', {
      params: {
        user_role: userRole
      }
    })
  },

  getSystemMessages: (category = null, page = 1, pageSize = 20) => {
    return request.get('/message/system/messages', {
      params: {
        category,
        page,
        page_size: pageSize
      }
    })
  },

  markSystemMessageRead: (messageId) => {
    return request.put(`/message/system/messages/${messageId}/read`)
  },

  markAllSystemMessagesRead: () => {
    return request.put('/message/system/messages/read-all')
  },

  getSystemTemplates: (category = null, page = 1, pageSize = 20) => {
    return request.get('/message/system/templates', {
      params: {
        category,
        page,
        page_size: pageSize
      }
    })
  },

  createSystemTemplate: (data) => {
    return request.post('/message/system/templates', data)
  },

  updateSystemTemplate: (templateId, data) => {
    return request.put(`/message/system/templates/${templateId}`, data)
  },

  deleteSystemTemplate: (templateId) => {
    return request.delete(`/message/system/templates/${templateId}`)
  },

  sendSystemMessage: (data) => {
    return request.post('/message/system/messages', data)
  },

  sendSystemMessageToMultiple: (data) => {
    return request.post('/message/system/messages/batch', data)
  }
}

export class WebSocketService {
  constructor() {
    this.socket = null
    this.callbacks = {}
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect(userId) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname
    const wsUrl = `${protocol}//${host}:8000/api/message/ws/${userId}`

    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.handleMessage(data)
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.socket.onclose = () => {
      console.log('WebSocket disconnected')
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++
          this.connect(userId)
        }, 1000 * Math.pow(2, this.reconnectAttempts))
      }
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  send(message) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    }
  }

  on(event, callback) {
    if (!this.callbacks[event]) {
      this.callbacks[event] = []
    }
    this.callbacks[event].push(callback)
  }

  off(event, callback) {
    if (this.callbacks[event]) {
      this.callbacks[event] = this.callbacks[event].filter(cb => cb !== callback)
    }
  }

  handleMessage(data) {
    const { type } = data
    if (this.callbacks[type]) {
      this.callbacks[type].forEach(callback => callback(data.data))
    }
  }

  sendMessage(conversationId, receiverId, content) {
    this.send({
      type: 'send_message',
      conversation_id: conversationId,
      receiver_id: receiverId,
      content
    })
  }

  markRead(conversationId) {
    this.send({
      type: 'mark_read',
      conversation_id: conversationId
    })
  }
}

export const wsService = new WebSocketService()