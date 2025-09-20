from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
import utils
import biliapi.video as video_api
import logging
import coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

TASK_EXPIRY_SECONDS = 10 * 24 * 60 * 60  # 10天

app = Flask(__name__)
CORS(app)

config=utils.load_json('config.json')

scheduler = BackgroundScheduler()
scheduler.start()

# 更新data的函数
def update_data(video_id, video_info, data):
    data["data"][video_id]["title"] = video_info["data"]["title"]
    data["data"][video_id]["desc"] = video_info["data"]["desc"]
    data["data"][video_id]["ownerName"] = video_info["data"]["owner"]["name"]
    data["data"][video_id]["ownerFace"] = video_info["data"]["owner"]["face"]
    data["data"][video_id]["pubdate"] = video_info["data"]["pubdate"]
    # 视频的实时基本数据
    data["data"][video_id]["view"] = video_info["data"]["stat"]["view"]
    data["data"][video_id]["danmaku"] = video_info["data"]["stat"]["danmaku"]
    data["data"][video_id]["reply"] = video_info["data"]["stat"]["reply"]
    data["data"][video_id]["like"] = video_info["data"]["stat"]["like"]
    data["data"][video_id]["coin"] = video_info["data"]["stat"]["coin"]
    data["data"][video_id]["share"] = video_info["data"]["stat"]["share"]
    # 收藏
    data["data"][video_id]["favorite"] = video_info["data"]["stat"].get("favorite", 0)
    # aid
    data["data"][video_id]["aid"] = video_info["data"]["aid"]
    # status设为running
    data["data"][video_id]["status"] = "running"
    return data

def GetData_task(video_id):
    try:
        logger.info(f"开始获取视频 {video_id} 的数据")
        if not utils.safe_video_id(video_id):
            logger.error(f"视频ID {video_id} 格式不合法，跳过任务")
            return
        data=utils.load_json('data.json')
        if int(time.time()) - data["data"][video_id].get("updated_at", 0) > TASK_EXPIRY_SECONDS:
            logger.info(f"视频 {video_id} 超过10天未更新任务，停止任务")
            # data.json中的status设为expired
            data["data"][video_id]["status"] = "expired"
            # 保存data.json
            utils.save_json('data.json', data)
            scheduler.remove_job(video_id)
            return
        video_info = video_api.get_video_info(video_id)
        logger.debug(f"视频信息: {video_info}")
        # 创建tasks目录
        if not os.path.exists("tasks"):
            os.makedirs("tasks")
        # 保存视频信息到tasks目录下的{video_id}.json文件
        # 如果没有这个文件就创建一个新的
        if not os.path.exists(f'tasks/{video_id}.json'):
            video_data = {"data":[{
                "timestamp": int(time.time()),
                "view": video_info["data"]["stat"]["view"],
                "danmaku": video_info["data"]["stat"]["danmaku"],
                "reply": video_info["data"]["stat"]["reply"],
                "like": video_info["data"]["stat"]["like"],
                "coin": video_info["data"]["stat"]["coin"],
                "share": video_info["data"]["stat"]["share"],
                "favorite": video_info["data"]["stat"].get("favorite", 0),
            }]}
        else:
            video_data = utils.load_json(f'tasks/{video_id}.json')
            video_data["data"].append({
                "timestamp": int(time.time()),
                "view": video_info["data"]["stat"]["view"],
                "danmaku": video_info["data"]["stat"]["danmaku"],
                "reply": video_info["data"]["stat"]["reply"],
                "like": video_info["data"]["stat"]["like"],
                "coin": video_info["data"]["stat"]["coin"],
                "share": video_info["data"]["stat"]["share"],
                "favorite": video_info["data"]["stat"].get("favorite", 0),
            })
        # 更新数据
        data = update_data(video_id, video_info, data)
        utils.save_json(f'tasks/{video_id}.json', video_data)
        utils.save_json('data.json', data)
        logger.info(f"视频 {video_id} 的数据已保存")
    except Exception as e:
        logger.error(f"获取视频 {video_id} 的数据失败: {e}")

# 没有data.json就创建一个新的
if not os.path.exists('data.json'):
    utils.save_json('data.json', {"data":{}})

# 遍历data.json中的所有任务
data=utils.load_json('data.json')
for video_id in data["data"].keys():
    logger.info(f"视频ID: {video_id}")
    try:
        # 如果updated_at离现在超过10天就跳过
        if int(time.time()) - data["data"][video_id].get("updated_at", 0) > 864000:
            logger.info(f"视频 {video_id} 超过10天未更新任务，跳过")
            data["data"][video_id]["status"] = "expired"
            utils.save_json('data.json', data)
            continue
        video_info = video_api.get_video_info(video_id)
        logger.debug(f"视频信息: {video_info}")
        # 更新数据
        data = update_data(video_id, video_info, data)
        utils.save_json('data.json', data)
        GetData_task(video_id)
        
        scheduler.add_job(
            func=GetData_task,
            trigger="interval",
            seconds=config.get("sleeptime", 60),
            args=[video_id],
            id=video_id,
            replace_existing=True
        )
        logger.info(f"任务 {video_id} 已添加到调度器")
    except Exception as e:
        logger.error(f"任务 {video_id} 添加失败: {e}")
    

@app.route('/api/get_data', methods=['GET'])
def get_data():
    # 获取video_id参数
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"ok": False, "msg": "缺少video_id参数"}), 400
    if not utils.safe_video_id(video_id):
        return jsonify({"ok": False, "msg": "video_id格式不合法"}), 400
    # 返回data.json的内容
    try:
        data = utils.load_json('data.json')["data"][video_id]
        video_data = utils.load_json(f'tasks/{video_id}.json')
    except (KeyError, FileNotFoundError) as e:
        logger.error(f"获取数据失败: {e}")
        return jsonify({"ok": False, "msg": "获取数据失败，可能是video_id错误或数据不存在", "code": 114}), 500
    except Exception as e:
        logger.error(f"意外错误: {e}")
        return jsonify({"ok": False, "msg": "服务器内部错误", "code": 500}), 500
    return jsonify({
        "ok": True,
        "msg": "成功",
        "data": data,
        "video_data": video_data["data"]
    })
    
# 创建任务api
@app.route('/api/create_task', methods=['POST'])
def create_task():
    video_id = request.json.get('video_id')
    if not video_id:
        return jsonify({"ok": False, "msg": "缺少video_id参数"}), 400
    if not utils.safe_video_id(video_id):
        return jsonify({"ok": False, "msg": "video_id格式不合法"}), 400
    data=utils.load_json('data.json')
    if video_id in data["data"].keys():
        return jsonify({"ok": False, "msg": "任务已存在"}), 400
    video_info = video_api.get_video_info(video_id)
    if "data" not in video_info:
        return jsonify({"ok": False, "msg": "视频不存在或获取视频信息失败"}), 400
    data["data"][video_id] = {
        "title": video_info["data"]["title"],
        "desc": video_info["data"]["desc"],
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        # 作者
        "ownerName": video_info["data"]["owner"]["name"],
        "ownerFace": video_info["data"]["owner"]["face"],
        # 视频发布时间
        "pubdate": video_info["data"]["pubdate"]
    }
    utils.save_json('data.json', data)
    GetData_task(video_id)
    scheduler.add_job(
        func=GetData_task,
        trigger="interval",
        seconds=config.get("sleeptime", 60),
        args=[video_id],
        id=video_id,
        replace_existing=True
    )
    return jsonify({"ok": True, "msg": "任务创建成功"})

# 更新任务api，更新updated_at时间
@app.route('/api/update_task', methods=['POST'])
def update_task():
    video_id = request.json.get('video_id')
    if not video_id:
        return jsonify({"ok": False, "msg": "缺少video_id参数"}), 400
    if not utils.safe_video_id(video_id):
        return jsonify({"ok": False, "msg": "video_id格式不合法"}), 400
    data=utils.load_json('data.json')
    if video_id not in data["data"].keys():
        return jsonify({"ok": False, "msg": "任务不存在"}), 400
    data["data"][video_id]["updated_at"] = int(time.time())
    data["data"][video_id]["status"] = "starting"
    utils.save_json('data.json', data)
    # 如果任务已经过期，重新添加任务
    if not scheduler.get_job(video_id):
        scheduler.add_job(
            func=GetData_task,
            trigger="interval",
            seconds=config.get("sleeptime", 60),
            args=[video_id],
            id=video_id,
            replace_existing=True
        )
    return jsonify({"ok": True, "msg": "任务更新成功"})


@app.route('/api/search_task', methods=['GET'])
def search_task():
    """
    搜索任务： 遍历data中的键名，看看有没有匹配的 继续匹配视频标题、视频描述、视频作者 去重返回视频信息，前端显示列表
    """
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"ok": False, "msg": "缺少keyword参数", "code": 400}), 400
    data=utils.load_json('data.json')
    results = []
    seen = set()
    for video_id, info in data["data"].items():
        if (keyword in video_id or
            keyword in info.get("title", "") or
            keyword in info.get("desc", "") or
            keyword in info.get("ownerName", "")):
            if video_id not in seen:
                results.append({
                    "video_id": video_id,
                    "title": info.get("title", ""),
                    "desc": info.get("desc", ""),
                    "created_at": info.get("created_at", 0),
                    "updated_at": info.get("updated_at", 0),
                    "ownerName": info.get("ownerName", ""),
                    "ownerFace": info.get("ownerFace", ""),
                    "pubdate": info.get("pubdate", 0)
                })
                seen.add(video_id)
    return jsonify({"ok": True, "msg": "搜索完成", "code": 0, "data": results})

if __name__ == '__main__':
    app.run(port=5080,host='0.0.0.0')
