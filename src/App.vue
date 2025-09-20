<template>
  <!-- 主页 -->
  <div v-if="pageType === 'main'">
    <el-page-header @back="goBack">
      <template #content>
        <span class="text-large font-600 mr-3"> 视频列表 </span>
      </template>
      <template #extra>
        <el-switch
          v-model="isDarkMode"
          class="theme-switch"
          inline-prompt
          :active-icon="Moon"
          :inactive-icon="Sunny"
          @change="toggleTheme"
        />
      </template>
    </el-page-header>
    <!-- 添加任务弹窗 -->
    <el-dialog
      title="新建任务"
      v-model="addTaskDialogVisible"
      width="30%"
      :before-close="
        () => {
          addTaskDialogVisible = false
          newTaskVideoId = ''
        }
      "
      @submit.prevent
    >
      <el-form>
        <el-form-item label="视频BVID" :label-width="80">
          <el-input v-model="newTaskVideoId" placeholder="请输入视频BVID，如：BVxxxx" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button
          @click="
            addTaskDialogVisible = false,
            newTaskVideoId = ''
          "
          >取 消</el-button
        >
        <el-button type="primary" @click="handleCreateTask" :loading="createLoading"
          >确 定</el-button
        >
      </template>
    </el-dialog>

    <el-card style="margin-top: 15px">
      <el-button type="primary" @click="addTaskDialogVisible = true">新建</el-button>
      <!-- 搜索框在最右边 -->
      <el-input
        v-model="keyword"
        placeholder="请输入搜索内容"
        clearable
        style="width: 220px; float: right"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch" type="primary">搜索</el-button>
        </template>
      </el-input>
      <el-table :data="tableData" style="width: 100%; margin-top: 10px" v-loading="tableLoading">
        <el-table-column prop="video_id" label="视频BVID" width="150" />
        <el-table-column prop="title" label="视频标题" width="200" />
        <el-table-column prop="desc" label="视频描述" show-overflow-tooltip />
        <el-table-column prop="ownerName" label="视频作者" width="150" />
        <el-table-column prop="pubdate" label="视频发布时间" width="150" />
        <el-table-column prop="updated_at" label="任务更新时间" width="150" />
        <!-- 操作列 -->
        <el-table-column label="操作" width="100" align="center">
          <!-- 使用作用域插槽 -->
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleView(scope.row)"> 查看 </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-link type="primary" href="https://github.com/wangdage12/bilibili-data-monitor" target="_blank" style="margin-top: 10px">Github仓库</el-link>
    </el-card>
  </div>
  <!-- 详情页 -->
  <div v-else-if="pageType === 'detail'">
    <el-page-header @back="goBack">
      <template #content>
        <span class="text-large font-600 mr-3"> 视频详情 </span>
      </template>
      <template #extra>
        <el-switch
          v-model="isDarkMode"
          class="theme-switch"
          inline-prompt
          :active-icon="Moon"
          :inactive-icon="Sunny"
          @change="toggleTheme"
        />
      </template>
    </el-page-header>
    <el-card style="margin-top: 15px">
      <el-descriptions title="视频信息" border>
        <el-descriptions-item label="视频名称"> {{ videoInfo.title }} </el-descriptions-item>
        <el-descriptions-item label="视频作者"> {{ videoInfo.ownerName }} </el-descriptions-item>
        <el-descriptions-item label="视频发布时间"> {{ videoInfo.pubdate }} </el-descriptions-item>
        <el-descriptions-item label="任务更新时间">
          {{ videoInfo.updated_at }}
        </el-descriptions-item>
        <el-descriptions-item label="视频描述"> {{ videoInfo.desc }} </el-descriptions-item>
        <!-- tag的type按照状态来设置 -->
        <el-descriptions-item label="获取状态">
          <el-tag :type="getStatusType(videoInfo.status)">{{ videoInfo.status }}</el-tag>
        </el-descriptions-item>
        <!-- 视频的基本数据 -->
        <el-descriptions-item label="播放量" width="120">
          {{ videoInfo.playCount }}
        </el-descriptions-item>
        <el-descriptions-item label="点赞数" width="120">
          {{ videoInfo.like }}
        </el-descriptions-item>
        <el-descriptions-item label="投币数" width="120">
          {{ videoInfo.coin }}
        </el-descriptions-item>
        <el-descriptions-item label="分享数" width="120">
          {{ videoInfo.share }}
        </el-descriptions-item>
        <el-descriptions-item label="弹幕数" width="120">
          {{ videoInfo.danmaku }}
        </el-descriptions-item>
        <el-descriptions-item label="评论数" width="120">
          {{ videoInfo.reply }}
        </el-descriptions-item>
        <el-descriptions-item label="收藏数" width="120">
          {{ videoInfo.favorite }}
        </el-descriptions-item>
        <el-descriptions-item label="AVID" width="120">
          {{ videoInfo.aid }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-card style="margin-top: 15px">
      <div class="chart-container">
        <v-chart class="chart" :option="option" autoresize />
      </div>
    </el-card>
    <el-card style="margin-top: 15px">
      <el-text size="large" tag="b">更新任务</el-text>
      <br />
      <el-text
        >任务有效期仅为创建后10天，超出10天以后将不再获取数据，你可以点击下方更新任务按钮，可以让有效期重置为10天以后</el-text
      >
      <br />
      <el-button
        type="primary"
        style="margin-top: 10px"
        @click="handleUpdateTask"
        :loading="updateLoading"
        >更新任务</el-button
      >
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { fetchTasks, createTask, fetchTask, updateTask } from './api'
import { ElMessage } from 'element-plus'
import { Moon, Sunny } from '@element-plus/icons-vue'

const keyword = ref('')

const tableLoading = ref(false)
const tableData = ref([])
const videoInfo = ref({
  title: '',
  ownerName: '',
  pubdate: '',
  updated_at: '',
  desc: '',
  status: '',
  playCount: 0,
  like: 0,
  coin: 0,
  share: 0,
  danmaku: 0,
  reply: 0,
  favorite: 0,
  aid: 0,
})

// 当前选中的视频id
const selectedVideoId = ref('')
// 更新任务按钮加载态
const updateLoading = ref(false)
// 添加任务按钮加载态
const createLoading = ref(false)
// 添加任务弹窗显示
const addTaskDialogVisible = ref(false)
// 添加任务输入的视频id
const newTaskVideoId = ref('')

const isDarkMode = ref(false)

// 切换主题
const toggleTheme = (value: boolean) => {
  const html = document.documentElement
  if (value) {
    html.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    html.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// 自动刷新定时器
const refreshTimer = ref<number | null>(null)

// 初始化主题并设置自动刷新
onMounted(() => {
  // 获取保存的主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
    toggleTheme(true)
  }

  // 如果在详情页面，设置自动刷新
  if (pageType.value === 'detail' && selectedVideoId.value) {
    refreshTimer.value = window.setInterval(() => {
      handleView({ video_id: selectedVideoId.value })
    }, 60000) // 每60秒刷新一次
  }
})

// 在组件卸载时清除定时器
onBeforeUnmount(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
})

// 视频历史数据
interface VideoData {
  coin: number
  danmaku: number
  like: number
  reply: number
  share: number
  timestamp: number
  view: number
  favorite: number
}
const video_datas = ref<VideoData[]>([])

const option = ref({
  title: {
    text: '视频历史数据',
  },
  tooltip: {
    trigger: 'axis',
  },
  legend: {
    data: ['播放量', '点赞数', '投币数', '分享数', '弹幕数', '评论数', '收藏数'],
  },
  xAxis: {
    type: 'category',
    data: [] as string[],
  },
  yAxis: {
    type: 'value',
    splitNumber: 10,
  },
  series: [
    { name: '播放量', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '点赞数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '投币数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '分享数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '弹幕数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '评论数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
    { name: '收藏数', type: 'line', smooth: true, data: [] as number[], symbol: 'none' },
  ],
  toolbox: {
    feature: {
      saveAsImage: {}, // 保存为图片
      dataView: {}, // 查看原始数据
      dataZoom: {}, // 区域缩放
    },
  },
  dataZoom: [
    {
      type: 'slider',
      show: true,
      xAxisIndex: [0],
    },
    {
      type: 'slider',
      show: true,
      yAxisIndex: [0],
      right: 100,
    },
    {
      type: 'inside',
      xAxisIndex: [0],
    },
    {
      type: 'inside',
      yAxisIndex: [0],
    },
  ],
})

watch(video_datas, (datas) => {
  if (!datas || datas.length === 0) return

  option.value.xAxis.data = datas.map((d) => {
    // 时间戳转日期字符串
    const date = new Date(d.timestamp * 1000)
    return date.toLocaleString()
  })
  option.value.series[0].data = datas.map((d) => d.view)
  option.value.series[1].data = datas.map((d) => d.like)
  option.value.series[2].data = datas.map((d) => d.coin)
  option.value.series[3].data = datas.map((d) => d.share)
  option.value.series[4].data = datas.map((d) => d.danmaku)
  option.value.series[5].data = datas.map((d) => d.reply)
  option.value.series[6].data = datas.map((d) => d.favorite)
})

// 页面类型
// main： 主页
// detail： 详情页
const pageType = ref('main')

const goBack = () => {
  if (pageType.value === 'detail') {
    pageType.value = 'main'
    // 清除自动刷新定时器
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  }
}
const handleSearch = () => {
  console.log('搜索内容:', keyword.value)
  if (!keyword.value) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  tableLoading.value = true
  // 调用搜索接口
  fetchTasks(keyword.value)
    .then((data) => {
      // 时间从时间戳转换为日期格式
      data.data.forEach((item: any) => {
        const date = new Date(item.updated_at * 1000)
        item.updated_at = date.toLocaleString()
        const pubDate = new Date(item.pubdate * 1000)
        item.pubdate = pubDate.toLocaleString()
      })
      tableData.value = data.data
    })
    .catch((error) => {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败：' + error.message)
    })
    .finally(() => {
      tableLoading.value = false
    })
}

const handleView = (row: any) => {
  console.log('查看视频:', row)

  // 获取视频信息
  fetchTask(row.video_id)
    .then((data) => {
      console.log('视频信息:', data)
      videoInfo.value = {
        title: data.data.title,
        ownerName: data.data.ownerName,
        pubdate: new Date(data.data.pubdate * 1000).toLocaleString(),
        updated_at: new Date(data.data.updated_at * 1000).toLocaleString(),
        desc: data.data.desc,
        status: data.data.status,
        playCount: data.data.view,
        like: data.data.like,
        coin: data.data.coin,
        share: data.data.share,
        danmaku: data.data.danmaku,
        reply: data.data.reply,
        favorite: data.data.favorite,
        aid: data.data.aid,
      }

      video_datas.value = data.video_data

      // 翻译status
      if (videoInfo.value.status === 'running') {
        videoInfo.value.status = '运行中'
      } else if (videoInfo.value.status === 'expired') {
        videoInfo.value.status = '已过期'
      } else if (videoInfo.value.status === 'starting') {
        videoInfo.value.status = '正在获取'
      } else if (videoInfo.value.status === 'failed') {
        videoInfo.value.status = '获取失败'
      } else {
        videoInfo.value.status = '未知状态'
      }

      selectedVideoId.value = row.video_id
    })
    .catch((error) => {
      console.error('获取视频信息失败:', error)
      ElMessage.error('获取视频信息失败：' + error.message)
    })

  // 跳转到详情页
  pageType.value = 'detail'

  // 开启自动刷新定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  refreshTimer.value = window.setInterval(() => {
    handleView({ video_id: selectedVideoId.value })
  }, 60000) // 每60秒刷新一次
}

// 根据状态返回tag的type
const getStatusType = (status: string) => {
  if (status === '运行中') {
    return 'success'
  } else if (status === '已过期') {
    return 'info'
  } else if (status === '正在获取') {
    return 'primary'
  } else if (status === '获取失败') {
    return 'danger'
  } else {
    return 'warning'
  }
}

const handleUpdateTask = () => {
  console.log('更新任务:', selectedVideoId.value)
  updateLoading.value = true
  // 调用更新任务接口
  updateTask(selectedVideoId.value)
    .then(() => {
      ElMessage.success('任务更新成功')
      // 再次获取视频信息
      handleView({ video_id: selectedVideoId.value })
    })
    .catch((error) => {
      console.error('任务更新失败:', error)
      ElMessage.error('任务更新失败：' + error.message)
    })
    .finally(() => {
      updateLoading.value = false
    })
}

// 创建任务
const handleCreateTask = () => {
  if (!newTaskVideoId.value) {
    ElMessage.warning('请输入视频BVID')
    return
  }
  createLoading.value = true
  createTask(newTaskVideoId.value)
    .then(() => {
      ElMessage.success('任务创建成功')
      addTaskDialogVisible.value = false
      keyword.value = newTaskVideoId.value
      newTaskVideoId.value = ''
      handleSearch()
    })
    .catch((error) => {
      console.error('任务创建失败:', error)
      ElMessage.error('任务创建失败：' + error.message)
    })
    .finally(() => {
      createLoading.value = false
    })
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 600px;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
