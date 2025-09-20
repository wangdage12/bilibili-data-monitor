# bilibili-data-monitor

**自动在线记录B站视频历史播放量等数据**  
通过右上角搜索即可搜索视频，可以搜索视频的大部分信息，搜不到可以新建，bvid可以通过视频分享链接后面的BVxxxxx得到
<img width="1905" height="370" alt="PixPin_2025-09-20_17-12-41 00_00_04_14 Still001" src="https://github.com/user-attachments/assets/7a933a93-8910-477a-9582-3d5f5483d835" />
<img width="1920" height="1080" alt="PixPin_2025-09-20_17-12-41 00_00_06_17 Still002" src="https://github.com/user-attachments/assets/c7644a24-0f97-4748-9e87-4598441916ad" />

> 有关该项目的动态，请查看[http://server.wdg.cloudns.ch:8088/category/bilibili-data-monitor/](http://server.wdg.cloudns.ch:8088/category/bilibili-data-monitor/)

## 启动和构建前端
> 需要先安装nodejs

### 安装依赖
```sh
npm install
```

### 启动开发服务器

```sh
npm run dev
```

### 构建静态文件

```sh
npm run build
```

## 启动api
> 需要先安装python >= 3.12

### Linux

```sh
pip install -r requirements.txt && python main.py
```

> 或者使用1panel

<img width="906" height="790" alt="PixPin_2025-09-20_17-52-49" src="https://github.com/user-attachments/assets/76797fa6-b31e-4dae-906c-4af18befcd6a" />


### Windows

```sh
pip install -r requirements.txt
python main.py
```

**启动以后向`http://localhost:5080`请求**

## 部署
构建好前端和准备好api以后，在dist目录中创建`apiconfig.json`，为了方便，该文件用于前端获取apiurl，请填写你的api地址  
**注意不要在apiurl末尾添加`/`**
```json
{
  "apiurl": "api地址"
}
```
*示例*
```json
{
  "apiurl": "http://localhost:5080/api"
}
```
之后，将dist目录中的所有文件上传到你的服务器网站目录中即可
