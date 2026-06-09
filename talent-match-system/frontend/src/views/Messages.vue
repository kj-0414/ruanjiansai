<template>
  <div class="message-center">
    <div class="message-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">消息</h2>
      </div>

      <div class="conversation-list">
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索"
            prefix-icon="el-icon-search"
            size="small"
          />
        </div>
        <el-scrollbar class="scrollbar">
          <div
            v-for="item in filteredConversations"
            :key="item.conversation.id"
            :class="['conversation-item', { active: selectedConversation?.id === item.conversation.id }]"
            @click="selectConversation(item)"
          >
            <div class="avatar">
              <span>{{ getAvatarText(item) }}</span>
            </div>
            <div class="conversation-info">
              <div class="conversation-title-row">
                <div class="conversation-title">{{ getConversationTitle(item) }}</div>
                <div class="time">{{ formatTime(item.last_message?.created_at) }}</div>
              </div>
              <div class="conversation-preview-row">
                <div class="conversation-preview">{{ item.last_message?.content || '暂无消息' }}</div>
                <div class="unread-badge" v-if="item.unread_count > 0">{{ item.unread_count > 99 ? '99+' : item.unread_count }}</div>
              </div>
            </div>
          </div>
          <div v-if="conversations.length === 0" class="empty-state">
            <p>暂无会话</p>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <div class="message-content">
      <div v-if="!selectedConversation" class="empty-chat">
        <div class="empty-icon">💬</div>
        <p>选择一个会话开始聊天</p>
      </div>

      <div v-else class="chat-area">
        <div class="chat-header">
          <div class="chat-avatar" @click="showOtherUserInfo">
            <span>{{ getOtherAvatarText() }}</span>
          </div>
          <div class="chat-info">
            <div class="chat-title">{{ getConversationTitle(selectedItem) }}</div>
            <div class="chat-subtitle">
              <el-tag v-if="selectedConversation.status === 'active'" type="success" size="small" effect="plain">在线</el-tag>
              <el-tag v-else-if="selectedConversation.status === 'closed'" type="info" size="small" effect="plain">已关闭</el-tag>
              <el-tag v-else type="warning" size="small" effect="plain">待确认</el-tag>
            </div>
          </div>
          <div class="chat-actions">
            <el-button size="small" icon="el-icon-more" circle />
          </div>
        </div>

        <el-scrollbar class="chat-messages" ref="messagesContainer">
          <div
            v-for="msg in chatMessages"
            :key="msg.id"
            :class="['message-item', { sent: isSentMessage(msg), received: !isSentMessage(msg) }]"
          >
            <div :class="['msg-wrapper', { sent: isSentMessage(msg), received: !isSentMessage(msg) }]">
              <div 
                class="msg-avatar" 
                :class="{ 'sent-avatar': isSentMessage(msg), 'received-avatar': !isSentMessage(msg) }"
                @click="isSentMessage(msg) ? showMyInfo() : showOtherUserInfo()"
              >
                <span>{{ isSentMessage(msg) ? (currentUserNickname.slice(0, 2) || currentUserPhone.slice(-4)) : (msg.sender_nickname?.slice(0, 2) || msg.sender_phone?.slice(-4) || getOtherAvatarText()) }}</span>
              </div>
              <div :class="['msg-content', { 'sent-content': isSentMessage(msg), 'received-content': !isSentMessage(msg) }]">
                <div v-if="!isSentMessage(msg)" class="msg-sender-name">{{ getSenderName(msg) }}</div>
                <div :class="['msg-bubble', { 'sent-bubble': isSentMessage(msg), 'received-bubble': !isSentMessage(msg) }]">
                  <div class="msg-text">{{ msg.content }}</div>
                </div>
                <div :class="['msg-time', { 'sent-time': isSentMessage(msg), 'received-time': !isSentMessage(msg) }]">
                  {{ formatMsgTime(msg.created_at) }}
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="isLoading" class="loading-more">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          
          <div v-if="chatMessages.length === 0 && !isLoading" class="no-messages">
            <p>暂无消息，开始聊天吧</p>
          </div>
        </el-scrollbar>

        <div class="chat-input-area">
          <el-button size="small" icon="el-icon-plus" circle />
          <el-input
            v-model="inputMessage"
            placeholder="输入消息..."
            @keyup.enter="sendChatMessage"
            :disabled="selectedConversation.status !== 'active'"
            size="medium"
            :maxlength="500"
            show-word-limit
          />
          <el-button type="primary" @click="sendChatMessage" :disabled="!inputMessage.trim() || selectedConversation.status !== 'active'" size="medium">
            发送
          </el-button>
        </div>
      </div>
    </div>

    <div class="pending-sidebar">
      <div class="pending-header">
        <span class="pending-title">待确认</span>
        <el-badge :value="pendingCount" />
      </div>
      <el-scrollbar class="scrollbar">
        <div
          v-for="item in pendingConversations"
          :key="item.conversation.id"
          class="pending-item"
        >
          <div class="pending-avatar">
            <span>{{ currentRole === 'company' ? (item.job_seeker?.nickname?.slice(0, 2) || item.job_seeker?.phone?.slice(-4) || '?') : (item.company?.nickname?.slice(0, 2) || item.company?.phone?.slice(-4) || '?') }}</span>
          </div>
          <div class="pending-info">
            <div class="pending-name">
              {{ currentRole === 'company' ? (item.job_seeker?.nickname || item.job_seeker?.phone || '未知') : (item.company?.nickname || item.company?.phone || '未知企业') }}
            </div>
            <div class="pending-desc">{{ item.job?.job_name }}</div>
          </div>
          <div class="pending-actions">
            <el-button type="primary" size="small" @click="activateConversation(item)">
              {{ currentRole === 'company' ? '确认简历' : '确认企业' }}
            </el-button>
          </div>
        </div>
        <div v-if="pendingConversations.length === 0" class="empty-state">
          <p>暂无待确认会话</p>
        </div>
      </el-scrollbar>
    </div>
  </div>

  <el-dialog title="用户信息" :visible.sync="showUserInfoDialog" width="300px">
    <div class="user-info-dialog">
      <div class="user-avatar-large">
        <span>{{ selectedUserInfo?.phone?.slice(-4) || '?' }}</span>
      </div>
      <div class="user-info-content">
        <div class="user-name">{{ selectedUserInfo?.phone || '未知用户' }}</div>
        <div class="user-role">{{ selectedUserInfo?.role === 'company' ? '企业用户' : '求职者' }}</div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage, ElDialog, ElLoading } from 'element-plus';
import { messageApi, wsService } from '../api/message';

const activeTab = ref('chat');
const searchKeyword = ref('');
const conversations = ref([]);
const pendingConversations = ref([]);
const selectedConversation = ref(null);
const selectedItem = ref(null);
const chatMessages = ref([]);
const inputMessage = ref('');
const unreadCounts = ref({ chat: 0, system: 0 });
const currentUserId = ref('');
const currentRole = ref('job_seeker');
const currentUserPhone = ref('');
const currentUserNickname = ref('');
const messagesContainer = ref(null);
const isLoading = ref(false);
const showUserInfoDialog = ref(false);
const selectedUserInfo = ref(null);

const pendingCount = computed(() => pendingConversations.value.length);

const filteredConversations = computed(() => {
  if (!searchKeyword.value)
    return conversations.value;
  return conversations.value.filter(item => {
    const title = getConversationTitle(item).toLowerCase();
    const preview = (item.last_message?.content || '').toLowerCase();
    return title.includes(searchKeyword.value.toLowerCase()) ||
    preview.includes(searchKeyword.value.toLowerCase());
  });
});

const getConversationTitle = (item) => {
  if (item.other_user) {
    return item.other_user.nickname || item.other_user.phone || '未知用户';
  }
  return '未知';
};

const getAvatarText = (item) => {
  if (item.other_user?.nickname) {
    const nickname = item.other_user.nickname;
    return nickname.slice(0, 2);
  }
  const title = getConversationTitle(item);
  return title.slice(-4);
};

const getOtherAvatarText = () => {
  if (selectedItem.value?.other_user) {
    if (selectedItem.value.other_user.nickname) {
      return selectedItem.value.other_user.nickname.slice(0, 2);
    }
    return selectedItem.value.other_user.phone?.slice(-4) || '对方';
  }
  return '对方';
};

const getSenderName = (msg) => {
  if (msg.sender_nickname) {
    return msg.sender_nickname;
  }
  if (msg.sender_phone) {
    return msg.sender_phone;
  }
  return getConversationTitle(selectedItem.value) || '对方';
};

const formatTime = (timestamp) => {
  if (!timestamp)
    return '';
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1)
    return '刚刚';
  if (minutes < 60)
    return `${minutes}分钟前`;
  if (hours < 24)
    return `${hours}小时前`;
  if (days < 7)
    return `${days}天前`;
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

const formatMsgTime = (timestamp) => {
  if (!timestamp)
    return '';
  const date = new Date(timestamp);
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

const isSentMessage = (msg) => {
  const senderId = String(msg.sender_id || msg.from_id || '');
  const currentId = String(currentUserId.value || '');
  
  return senderId === currentId;
};

const showMyInfo = () => {
  selectedUserInfo.value = {
    phone: currentUserPhone.value,
    role: currentRole.value
  };
  showUserInfoDialog.value = true;
};

const showOtherUserInfo = () => {
  selectedUserInfo.value = {
    phone: selectedItem.value?.other_user?.phone || '',
    role: currentRole.value === 'job_seeker' ? 'company' : 'job_seeker'
  };
  showUserInfoDialog.value = true;
};

const loadConversations = async () => {
  const role = localStorage.getItem('role') || 'job_seeker';
  currentRole.value = role;
  try {
    const response = await messageApi.getUserConversations(role);
    conversations.value = response.data || [];
  }
  catch (error) {
    console.error('加载会话失败:', error);
  }
};

const loadPendingConversations = async () => {
  try {
    if (currentRole.value === 'company') {
      const response = await messageApi.getPendingConversations();
      pendingConversations.value = response.data || [];
    } else {
      const response = await messageApi.getPendingConversationsForJobSeeker();
      pendingConversations.value = response.data || [];
    }
  }
  catch (error) {
    console.error('加载待确认会话失败:', error);
  }
};

const activateConversation = async (item) => {
  try {
    if (currentRole.value === 'company') {
      await messageApi.activateConversation(item.conversation.id);
      ElMessage.success('已确认简历');
    } else {
      await messageApi.activateConversationByJobSeeker(item.conversation.id);
      ElMessage.success('已确认企业资质');
    }
    await loadPendingConversations();
    await loadConversations();

    const conversationId = item.conversation.id;
    const activatedItem = conversations.value.find(c => c.conversation.id === conversationId);
    if (activatedItem) {
      selectedConversation.value = activatedItem.conversation;
      selectedItem.value = activatedItem;
      await loadConversationMessages(conversationId);
      messageApi.markConversationRead(conversationId);
    }
  }
  catch (error) {
    ElMessage.error(error.response?.data?.detail || '开启会话失败');
  }
};

const selectConversation = async (item) => {
  selectedConversation.value = item.conversation;
  selectedItem.value = item;
  await loadConversationMessages(item.conversation.id);
  messageApi.markConversationRead(item.conversation.id);
};

const loadConversationMessages = async (conversationId) => {
  isLoading.value = true;
  try {
    const response = await messageApi.getConversationMessages(conversationId);
    chatMessages.value = (response.data || []).reverse();
    await nextTick(() => {
      scrollToBottom();
    });
  }
  catch (error) {
    console.error('加载消息失败:', error);
    ElMessage.error('加载消息失败');
  } finally {
    isLoading.value = false;
  }
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    const scrollEl = messagesContainer.value.$el.querySelector('.el-scrollbar__wrap');
    if (scrollEl) {
      scrollEl.scrollTop = scrollEl.scrollHeight;
    }
  }
};

const sendChatMessage = async () => {
  if (!inputMessage.value.trim() || !selectedConversation.value)
    return;
  if (selectedConversation.value.status !== 'active') {
    ElMessage.warning('会话尚未开启');
    return;
  }
  const receiverId = selectedItem.value.other_user?.id;
  if (!receiverId)
    return;
  try {
    const response = await messageApi.sendMessage(selectedConversation.value.id, receiverId, inputMessage.value.trim(), currentRole.value);
    inputMessage.value = '';
    if (response.data) {
      chatMessages.value.push(response.data);
      await nextTick(() => {
        scrollToBottom();
      });
    } else {
      await loadConversationMessages(selectedConversation.value.id);
    }
  }
  catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送失败');
  }
};

const handleNewMessage = (message) => {
  if (selectedConversation.value && selectedConversation.value.id === message.conversation_id) {
    chatMessages.value.push(message);
    setTimeout(() => {
      scrollToBottom();
    }, 100);
  }
  loadConversations();
};

onMounted(() => {
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  currentUserId.value = user?.id || user?.phone || localStorage.getItem('userId') || '';
  currentUserPhone.value = user?.phone || currentUserId.value;
  currentUserNickname.value = user?.nickname || '';
  currentRole.value = localStorage.getItem('role') || 'job_seeker';

  loadConversations();
  loadPendingConversations();

  if (currentUserId.value) {
    wsService.connect(currentUserId.value);
    wsService.on('new_message', handleNewMessage);
  }
});

onUnmounted(() => {
  wsService.off('new_message', handleNewMessage);
  wsService.disconnect();
});
</script>

<style scoped>
.message-center {
  display: flex;
  height: 100vh;
  background: #fff;
}

.message-sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.conversation-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-box {
  padding: 10px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 20px;
  background: #f5f5f5;
}

.scrollbar {
  flex: 1;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f5f5f5;
}

.conversation-item:hover {
  background: #f8f9fa;
}

.conversation-item.active {
  background: #e0f2fe;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  margin-right: 12px;
  flex-shrink: 0;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time {
  font-size: 11px;
  color: #9ca3af;
  flex-shrink: 0;
  margin-left: 8px;
}

.conversation-preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-preview {
  font-size: 12px;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.unread-badge {
  background: #ef4444;
  color: white;
  font-size: 10px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  margin-left: 8px;
  flex-shrink: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
  font-size: 14px;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-chat p {
  font-size: 16px;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  margin-right: 12px;
  cursor: pointer;
  transition: transform 0.2s;
}

.chat-avatar:hover {
  transform: scale(1.05);
}

.chat-info {
  flex: 1;
}

.chat-title {
  font-size: 15px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2px;
}

.chat-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.message-item {
  margin-bottom: 16px;
  display: flex;
}

.message-item.sent {
  justify-content: flex-end;
}

.message-item.received {
  justify-content: flex-start;
}

.msg-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.msg-wrapper.sent {
  justify-content: flex-end;
  flex-direction: row-reverse;
}

.msg-wrapper.received {
  justify-content: flex-start;
}

.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.msg-avatar:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sent-avatar {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.received-avatar {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.msg-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.sent-content {
  align-items: flex-end;
}

.received-content {
  align-items: flex-start;
}

.msg-sender-name {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  padding-left: 4px;
}

.msg-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.2s;
}

.msg-bubble:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.sent-bubble {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-bottom-right-radius: 4px;
}

.received-bubble {
  background: #fff;
  border-bottom-left-radius: 4px;
  border: 1px solid #e5e7eb;
}

.msg-text {
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.sent-bubble .msg-text {
  color: #fff;
}

.received-bubble .msg-text {
  color: #1f2937;
}

.msg-time {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 6px;
}

.sent-time {
  text-align: right;
}

.received-time {
  text-align: left;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  gap: 8px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-more span {
  font-size: 12px;
  color: #9ca3af;
}

.no-messages {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.no-messages p {
  font-size: 14px;
}

.chat-input-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.chat-input-area :deep(.el-input__wrapper) {
  flex: 1;
  border-radius: 25px;
}

.chat-input-area :deep(.el-button) {
  border-radius: 20px;
}

.pending-sidebar {
  width: 240px;
  background: #fff;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.pending-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.pending-title {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.pending-item {
  display: flex;
  align-items: center;
  padding: 12px 12px;
  border-bottom: 1px solid #f5f5f5;
  gap: 10px;
}

.pending-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  flex-shrink: 0;
}

.pending-info {
  flex: 1;
  min-width: 0;
}

.pending-name {
  font-size: 13px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2px;
}

.pending-desc {
  font-size: 11px;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pending-actions {
  flex-shrink: 0;
}

.pending-actions .el-button {
  border-radius: 14px;
  font-size: 12px;
}

.user-info-dialog {
  text-align: center;
  padding: 20px;
}

.user-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  margin: 0 auto 16px;
}

.user-info-content {
  text-align: center;
}

.user-name {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
}

.user-role {
  font-size: 14px;
  color: #6b7280;
}
</style>