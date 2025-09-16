import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/theme-chalk/dark/css-vars.css'

// 引入 ECharts 核心模块
import { use } from 'echarts/core'
// 引入图表类型
import { LineChart } from 'echarts/charts'
// 引入组件
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
} from 'echarts/components'
// 引入 Canvas 渲染器
import { CanvasRenderer } from 'echarts/renderers'
// Vue 封装的 ECharts 组件
import ECharts from 'vue-echarts'

// 注册必须的组件
use([
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
])

createApp(App).use(ElementPlus, { locale: zhCn }).component('v-chart', ECharts).mount('#app')
