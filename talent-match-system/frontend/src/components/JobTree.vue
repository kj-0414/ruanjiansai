<template>
  <div class="ability-tree">
    <el-card class="tree-card" shadow="hover" :body-style="{ padding: '0' }">
      <template #header>
        <div class="card-header">
          <h3 class="card-title">岗位需求树状图谱</h3>
          <el-button type="primary" size="small" @click="refreshTree">
            刷新
          </el-button>
        </div>
      </template>
      <div class="tree-container" ref="treeContainer"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { jobAbilityApi } from '../api/jobAbility';

const props = defineProps({
  jobId: {
    type: [Number, String],
    required: true
  }
});

const treeContainer = ref(null);
let treeChart = null;
let jobTreeData = null; // 保存原始岗位需求树数据
let expandedNodes = new Set(); // 保存展开状态的节点
let allLeafNodesExpanded = true; // 所有叶子节点是否展开

// 检查节点是否是叶子节点
const isLeafNode = (nodeName, data) => {
  const findNode = (node) => {
    if (node.name === nodeName) {
      return node;
    }
    if (node.children && node.children.length > 0) {
      for (const child of node.children) {
        const found = findNode(child);
        if (found) {
          return found;
        }
      }
    }
    return null;
  };
  
  const node = findNode(data);
  return !node || !node.children || node.children.length === 0;
};

// 展开所有父节点
const expandAllParentNodes = (node) => {
  if (!node) return;
  
  console.log('展开节点:', node.name);
  expandedNodes.add(node.name);
  
  if (node.children && Array.isArray(node.children) && node.children.length > 0) {
    console.log('节点', node.name, '有', node.children.length, '个子节点');
    for (const child of node.children) {
      expandAllParentNodes(child);
    }
  } else {
    console.log('节点', node.name, '没有子节点');
  }
};

const initChart = () => {
  if (treeContainer.value && !treeChart) {
    treeChart = echarts.init(treeContainer.value);
    console.log('ECharts实例创建成功');
    console.log('容器大小:', treeContainer.value.clientWidth, 'x', treeContainer.value.clientHeight);
    console.log('ECharts实例大小:', treeChart.getWidth(), 'x', treeChart.getHeight());
    
    // 添加点击事件监听器
    treeChart.on('click', handleNodeClick);
  }
};

const handleNodeClick = (params) => {
  if (params.dataType === 'node') {
    const nodeName = params.name;
    
    // 点击岗位需求根节点，切换所有叶子节点的展开状态
    if (nodeName === '岗位需求') {
      allLeafNodesExpanded = !allLeafNodesExpanded;
      expandedNodes.clear(); // 清空展开状态
      if (allLeafNodesExpanded) {
        // 如果要展开所有叶子节点，需要展开所有中间节点
        expandAllParentNodes(jobTreeData);
      } else {
        // 如果要收起所有叶子节点，只保留一级节点
        expandedNodes.add('岗位需求');
      }
      // 延迟更新图表，避免在ECharts主进程执行期间调用
      setTimeout(() => {
        updateChart(jobTreeData);
      }, 50);
    } else {
      // 检查是否是叶子节点（最后一级）
      if (!isLeafNode(nodeName, jobTreeData)) {
        // 切换节点的展开状态
        if (expandedNodes.has(nodeName)) {
          expandedNodes.delete(nodeName);
        } else {
          expandedNodes.add(nodeName);
        }
        // 延迟更新图表，避免在ECharts主进程执行期间调用
        setTimeout(() => {
          updateChart(jobTreeData);
        }, 50);
      }
    }
  }
};

const refreshTree = async () => {
  try {
    console.log('刷新树状图，jobId:', props.jobId);
    const response = await jobAbilityApi.getJobAbilityTree(props.jobId);
    console.log('获取岗位需求树响应:', response);
    
    if (response && response.data && response.data.data) {
      jobTreeData = response.data.data;
    } else if (response && response.data) {
      // 如果响应已经是数据对象（没有外层包装），直接使用
      jobTreeData = response.data;
    } else {
      // 使用默认数据
      jobTreeData = getDefaultTreeData();
    }
    
    expandedNodes.clear();
    expandAllParentNodes(jobTreeData);
    allLeafNodesExpanded = true;
    
    // 延迟更新图表，确保ECharts实例已经完全初始化
    setTimeout(() => {
      updateChart(jobTreeData);
    }, 50);
  } catch (error) {
    console.error('刷新树状图失败:', error);
    ElMessage.error('刷新树状图失败');
    // 出错时使用默认数据
    jobTreeData = getDefaultTreeData();
    expandedNodes.clear();
    expandAllParentNodes(jobTreeData);
    allLeafNodesExpanded = true;
    // 延迟更新图表，确保ECharts实例已经完全初始化
    setTimeout(() => {
      updateChart(jobTreeData);
    }, 50);
  }
};

// 获取默认树状图数据
const getDefaultTreeData = () => {
  return {
    name: '岗位需求',
    children: [
      {
        name: '学历背景',
        children: [
          { name: '学历要求: 本科及以上' }
        ]
      },
      {
        name: '专业技能',
        children: [
          { name: '前端开发: Vue.js, React, JavaScript' },
          { name: '后端开发: Node.js, Python' },
          { name: '数据库: MySQL, MongoDB' },
          { name: '工具: Git, Webpack' }
        ]
      },
      {
        name: '证书',
        children: [
          { name: '计算机二级证书' },
          { name: '英语四级证书' }
        ]
      },
      {
        name: '工作经历',
        children: [
          { name: '经验要求: 3年以上' }
        ]
      },
      {
        name: '项目经历',
        children: [
          { name: '企业级项目经验' },
          { name: '团队协作经验' }
        ]
      }
    ]
  };
};

const updateChart = (data) => {
  // 确保图表实例存在
  if (!treeChart) {
    initChart();
  }
  
  if (treeChart) {
    let nodes = [];
    let links = [];
    let nodeNames = new Set(); // 用于检查节点名称是否唯一
    
    if (data) {
      // 从真实数据构建节点和链接，考虑展开状态
      const buildNodes = (node, parent = null, depth = 0) => {
        // 确保节点名称唯一
        if (nodeNames.has(node.name)) {
          console.warn(`重复的节点名称: ${node.name}`);
          return;
        }
        nodeNames.add(node.name);
        
        // 计算节点大小和样式
        let symbolSize = 60;
        let itemStyle = { color: '#fff', borderColor: '#a6c8e0', borderWidth: 2 };
        let value = 100;
        
        if (depth === 1) {
          symbolSize = 45;
          itemStyle = { color: '#a6c8e0' };
          value = 50;
        } else if (depth > 1) {
          symbolSize = 25;
          itemStyle = { color: '#fff', borderColor: '#a6c8e0', borderWidth: 2 };
          value = 20;
        }
        
        // 添加当前节点
        nodes.push({
          id: node.name, // 添加id属性，确保唯一性
          name: node.name,
          value: value,
          symbolSize: symbolSize,
          itemStyle: itemStyle
        });
        
        // 添加与父节点的链接
        if (parent) {
          links.push({
            source: parent.name,
            target: node.name
          });
        }
        
        // 递归处理子节点，只有当节点处于展开状态时
        if (node.children && node.children.length > 0 && expandedNodes.has(node.name)) {
          node.children.forEach(child => {
            buildNodes(child, node, depth + 1);
          });
        }
      };
      
      buildNodes(data);
    }
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}'
      },
      series: [
        {
          type: 'graph',
          layout: 'circular',
          data: nodes,
          links: links,
          roam: true,
          label: {
            show: true,
            position: 'inside',
            fontSize: 12,
            color: '#333',
            align: 'center',
            verticalAlign: 'middle'
          },
          symbol: 'circle',
          lineStyle: {
            color: '#ccc',
            width: 1,
            curveness: 0.1 // 增加曲线度，使连线更加美观
          },
          circular: {
            rotateLabel: true // 旋转标签，避免标签重叠
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 2
            }
          }
        }
      ]
    };
    
    try {
      // 延迟执行setOption，避免在ECharts主进程执行期间调用
      setTimeout(() => {
        if (treeChart) {
          treeChart.setOption(option, true); // 第二个参数设为true，强制更新所有数据
          console.log('图表更新成功');
          
          // 延迟执行resize，避免在ECharts主进程执行期间调用
          setTimeout(() => {
            if (treeChart) {
              treeChart.resize();
              console.log('图表大小调整成功');
            }
          }, 50);
        }
      }, 50);
    } catch (error) {
      console.error('图表更新失败:', error);
    }
  } else {
    console.error('ECharts实例未创建');
  }
};

const handleResize = () => {
  if (treeChart) {
    treeChart.resize();
  }
};

onMounted(() => {
  console.log('组件挂载，初始化图表');
  console.log('treeContainer.value:', treeContainer.value);
  // 延迟初始化，确保DOM已经渲染完成
  setTimeout(() => {
    initChart();
    refreshTree();
  }, 100);
  window.addEventListener('resize', handleResize);
});

// 监听jobId变化
watch(() => props.jobId, (newJobId) => {
  console.log('jobId变化，刷新树状图');
  refreshTree();
});

onUnmounted(() => {
  if (treeChart) {
    treeChart.dispose();
    treeChart = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.ability-tree {
  width: 100%;
}

.tree-card {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.tree-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.tree-container {
  width: 100%;
  height: 700px;
  position: relative;
  overflow: hidden;
}
</style>