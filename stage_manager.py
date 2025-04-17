import requests
import json
import os
from datetime import datetime, timedelta
import time


class StageDataManager:
    def __init__(self, cache_dir='./cache'):
        self.base_url = 'https://ota.maa.plus/MaaAssistantArknights/api/'  # MAA API基础URL
        self.cache_dir = cache_dir
        self.cached_stage_data = None
        self.cached_stage_data_time = 0
        self.cache_lifespan = 24 * 60 * 60  # 24小时，单位秒

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, 'gui'), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, 'resource'), exist_ok=True)

    def get_stage_data(self, client_type='Official', force_refresh=False):
        """获取关卡数据，优先使用缓存"""
        # 检查缓存是否有效
        if not force_refresh and self.is_cache_valid():
            return self.cached_stage_data

        try:
            # 获取活动关卡数据
            activity_data = self.fetch_api_with_cache('gui/StageActivity.json')

            # 获取任务资源数据
            tasks_data = self.fetch_api_with_cache('resource/tasks.json')

            # 解析关卡数据
            stage_data = self.parse_stage_data(activity_data, tasks_data, client_type)

            # 更新缓存
            self.cached_stage_data = stage_data
            self.cached_stage_data_time = time.time()

            return stage_data
        except Exception as e:
            print(f"Error fetching stage data: {e}")
            # 尝试从本地缓存文件加载
            return self.load_from_local_cache(client_type)

    def is_cache_valid(self):
        """判断缓存是否仍然有效"""
        return (self.cached_stage_data is not None and
                (time.time() - self.cached_stage_data_time < self.cache_lifespan))

    def fetch_api_with_cache(self, api_path):
        """从API获取数据并缓存到本地文件"""
        cache_file_path = os.path.join(self.cache_dir, api_path)
        cache_dir = os.path.dirname(cache_file_path)

        # 创建缓存子目录
        os.makedirs(cache_dir, exist_ok=True)

        try:
            # 从API获取数据
            response = requests.get(f"{self.base_url}{api_path}")
            response.raise_for_status()  # 如果响应包含错误状态码，将引发异常
            data = response.json()

            # 保存到缓存文件
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except Exception as e:
            print(f"Error fetching {api_path}: {e}")

            # 尝试从本地缓存文件加载
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as cache_error:
                print(f"Error reading cache {cache_file_path}: {cache_error}")
                return None

    def load_from_local_cache(self, client_type='Official'):
        """从本地缓存文件加载数据"""
        try:
            activity_path = os.path.join(self.cache_dir, 'gui/StageActivity.json')
            with open(activity_path, 'r', encoding='utf-8') as f:
                activity_data = json.load(f)

            return self.parse_stage_data(activity_data, None, client_type)
        except Exception as e:
            print(f"Error loading from local cache: {e}")
            return {'permanent': self.initialize_permanent_stages(), 'activity': []}

    def parse_stage_data(self, activity_data, tasks_data, client_type):
        """解析关卡数据"""
        stages = {
            'permanent': self.initialize_permanent_stages(),
            'activity': []
        }

        # 如果没有活动数据，直接返回常驻关卡
        if not activity_data or client_type not in activity_data:
            return stages

        # 解析活动关卡
        client_data = activity_data[client_type]

        # 添加活动关卡
        if 'sideStoryStage' in client_data and isinstance(client_data['sideStoryStage'], list):
            stages['activity'] = []
            for stage in client_data['sideStoryStage']:
                stage_info = {
                    'display': stage.get('Display', ''),
                    'value': stage.get('Value', ''),
                    'drop': stage.get('Drop', ''),
                }

                if 'Activity' in stage:
                    activity = stage['Activity']
                    stage_info['activity'] = {
                        'tip': activity.get('Tip', ''),
                        'stageName': activity.get('StageName', ''),
                        'utcStartTime': self.parse_datetime(activity, 'UtcStartTime'),
                        'utcExpireTime': self.parse_datetime(activity, 'UtcExpireTime'),
                        'timeZone': activity.get('TimeZone', 0)
                    }

                stages['activity'].append(stage_info)

        # 添加资源收集信息
        if 'resourceCollection' in client_data:
            rc = client_data['resourceCollection']
            stages['resourceCollection'] = {
                'tip': rc.get('Tip', ''),
                'utcStartTime': self.parse_datetime(rc, 'UtcStartTime'),
                'utcExpireTime': self.parse_datetime(rc, 'UtcExpireTime'),
                'timeZone': rc.get('TimeZone', 0),
                'isResourceCollection': True
            }

        return stages

    def initialize_permanent_stages(self):
        """初始化常驻关卡数据"""
        return [
            {'display': "1-7", 'value': "1-7"},
            {'display': "R8-11", 'value': "R8-11"},
            {'display': "12-17-HARD", 'value': "12-17-HARD"},
            {'display': "CE-6", 'value': "CE-6", 'openDays': [1, 3, 5, 6]},  # 周二、四、六、日
            {'display': "AP-5", 'value': "AP-5", 'openDays': [0, 3, 5, 6]},  # 周一、四、六、日
            {'display': "CA-5", 'value': "CA-5", 'openDays': [1, 2, 4, 6]},  # 周二、三、五、日
            {'display': "LS-6", 'value': "LS-6", 'openDays': []},  # 全天开放
            {'display': "SK-5", 'value': "SK-5", 'openDays': [0, 2, 4, 5]},  # 周一、三、五、六
            {'display': "Annihilation", 'value': "Annihilation"},
            # 芯片本
            {'display': "PR-A-1", 'value': "PR-A-1", 'openDays': [0, 3, 4, 6]},
            {'display': "PR-A-2", 'value': "PR-A-2", 'openDays': [0, 3, 4, 6]},
            {'display': "PR-B-1", 'value': "PR-B-1", 'openDays': [0, 1, 4, 5]},
            {'display': "PR-B-2", 'value': "PR-B-2", 'openDays': [0, 1, 4, 5]},
            {'display': "PR-C-1", 'value': "PR-C-1", 'openDays': [2, 3, 5, 6]},
            {'display': "PR-C-2", 'value': "PR-C-2", 'openDays': [2, 3, 5, 6]},
            {'display': "PR-D-1", 'value': "PR-D-1", 'openDays': [1, 2, 5, 6]},
            {'display': "PR-D-2", 'value': "PR-D-2", 'openDays': [1, 2, 5, 6]}
        ]

    def parse_datetime(self, data, key):
        """解析日期时间"""
        if not data or key not in data:
            return None

        try:
            # 格式："yyyy/MM/dd HH:mm:ss"
            date_str = data[key]
            date_format = "%Y/%m/%d %H:%M:%S"
            date = datetime.strptime(date_str, date_format)

            # 调整时区
            time_zone = data.get('TimeZone', 0)
            date = date - timedelta(hours=time_zone)

            return date.isoformat()
        except Exception as e:
            print(f"Error parsing date {key}: {e}")
            return None

    def is_stage_open(self, stage, current_day_of_week):
        """判断关卡是否开放"""
        # 如果是活动关卡
        if 'activity' in stage:
            now = datetime.now()

            # 检查活动是否在有效期内
            if stage['activity'].get('utcStartTime') and stage['activity'].get('utcExpireTime'):
                start_time = datetime.fromisoformat(stage['activity']['utcStartTime'])
                end_time = datetime.fromisoformat(stage['activity']['utcExpireTime'])

                if start_time <= now <= end_time:
                    return True

            # 活动过期但是资源收集
            if stage['activity'].get('isResourceCollection'):
                # 检查开放日
                return self.is_day_open(stage, current_day_of_week)

            return False

        # 常驻关卡
        return self.is_day_open(stage, current_day_of_week)

    def is_day_open(self, stage, current_day_of_week):
        """检查当天是否开放"""
        # 没有指定开放日则全天开放
        if 'openDays' not in stage or not stage['openDays']:
            return True

        return current_day_of_week in stage['openDays']

    def get_open_stages(self, day_of_week=None):
        """获取开放关卡列表"""
        if day_of_week is None:
            # 注意：Python的weekday()返回0-6，对应周一到周日
            # 转换为0-6对应周日到周六
            current_weekday = datetime.now().weekday()
            day_of_week = 6 if current_weekday == 6 else current_weekday + 1

        if not self.cached_stage_data:
            self.get_stage_data()

        all_stages = []

        # 添加常驻关卡
        if 'permanent' in self.cached_stage_data:
            all_stages.extend(self.cached_stage_data['permanent'])

        # 添加活动关卡
        if 'activity' in self.cached_stage_data:
            all_stages.extend(self.cached_stage_data['activity'])

        # 过滤出开放的关卡
        return [stage for stage in all_stages if self.is_stage_open(stage, day_of_week)]