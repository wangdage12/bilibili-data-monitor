// 后端api

// 获取API基础URL
export async function getApiBaseUrl(): Promise<string> {
  const config = await (await fetch('/apiconfig.json')).json()
  return config.apiurl
}

// 搜索api
// http://127.0.0.1:5080/api/search_task?keyword=xxx
export async function getApiSearchTask(): Promise<string> {
  return `${await getApiBaseUrl()}/search_task`
}

// 新建任务api
// http://127.0.0.1:5080/api/create_task
export async function getApiCreateTask(): Promise<string> {
  return `${await getApiBaseUrl()}/create_task`
}

// 查看任务api
// http://127.0.0.1:5080/api/get_task?video_id=xxx
export async function getApiViewTask(): Promise<string> {
  return `${await getApiBaseUrl()}/get_data`
}

// 更新任务api
// /api/update_task
export async function getApiUpdateTask(): Promise<string> {
  return `${await getApiBaseUrl()}/update_task`
}

// 请求函数

// 搜索任务
export async function fetchTasks(keyword: string) {
  const url = `${await getApiSearchTask()}?keyword=${encodeURIComponent(keyword)}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('API错误：' + (await response.json()).msg)
  }
  const data = await response.json()
  return data
}

// 创建任务
export async function createTask(video_id: string) {
  const response = await fetch(await getApiCreateTask(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ video_id: video_id }),
  })
  if (!response.ok) {
    throw new Error('API错误：' + (await response.json()).msg)
  }
  const data = await response.json()
  return data
}

// 查看任务
export async function fetchTask(video_id: string) {
  const url = `${await getApiViewTask()}?video_id=${encodeURIComponent(video_id)}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('API错误：' + (await response.json()).msg)
  }
  const data = await response.json()
  return data
}

// 更新任务
export async function updateTask(video_id: string) {
  const response = await fetch(await getApiUpdateTask(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ video_id }),
  })
  if (!response.ok) {
    throw new Error('API错误：' + (await response.json()).msg)
  }
  const data = await response.json()
  return data
}
