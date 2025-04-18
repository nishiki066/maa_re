import unittest
import os
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from stage_manager import StageDataManager


class TestStageManager(unittest.TestCase):
    def setUp(self):
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.stage_manager = StageDataManager(cache_dir=self.temp_dir)

        # 创建测试缓存目录
        os.makedirs(os.path.join(self.temp_dir, 'gui'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'resource'), exist_ok=True)

        # 准备测试数据
        self.prepare_test_data()

    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)

    def prepare_test_data(self):
        # 创建模拟的StageActivity.json
        stage_activity = {
            "Official": {
                "sideStoryStage": [
                    {
                        "Display": "EA-8",
                        "Value": "EA-8",
                        "Drop": "31073",
                        "MinimumRequired": "v5.10.0",
                        "Activity": {
                            "Tip": "SideStory「挽歌燃烧殆尽」",
                            "StageName": "挽歌燃烧殆尽",
                            "UtcStartTime": (datetime.now() - timedelta(days=5)).strftime("%Y/%m/%d %H:%M:%S"),
                            "UtcExpireTime": (datetime.now() + timedelta(days=5)).strftime("%Y/%m/%d %H:%M:%S"),
                            "TimeZone": 8
                        }
                    },
                    {
                        "Display": "EA-7",
                        "Value": "EA-7",
                        "Drop": "31043",
                        "MinimumRequired": "v5.10.0",
                        "Activity": {
                            "Tip": "SideStory「挽歌燃烧殆尽」",
                            "StageName": "挽歌燃烧殆尽",
                            "UtcStartTime": (datetime.now() - timedelta(days=5)).strftime("%Y/%m/%d %H:%M:%S"),
                            "UtcExpireTime": (datetime.now() + timedelta(days=5)).strftime("%Y/%m/%d %H:%M:%S"),
                            "TimeZone": 8
                        }
                    }
                ],
                "resourceCollection": {
                    "Tip": "资源收集限时全天开放",
                    "UtcStartTime": (datetime.now() - timedelta(days=10)).strftime("%Y/%m/%d %H:%M:%S"),
                    "UtcExpireTime": (datetime.now() + timedelta(days=10)).strftime("%Y/%m/%d %H:%M:%S"),
                    "TimeZone": 8,
                    "IsResourceCollection": True
                }
            }
        }

        # 保存模拟数据到缓存文件
        with open(os.path.join(self.temp_dir, 'gui/StageActivity.json'), 'w', encoding='utf-8') as f:
            json.dump(stage_activity, f, ensure_ascii=False, indent=2)

    def test_load_from_cache(self):
        """测试从缓存加载数据"""
        stage_data = self.stage_manager.load_from_local_cache()
        self.assertIsNotNone(stage_data)
        self.assertIn('permanent', stage_data)
        self.assertIn('activity', stage_data)

        # 验证是否正确解析了活动关卡
        self.assertEqual(len(stage_data['activity']), 2)
        self.assertEqual(stage_data['activity'][0]['display'], 'EA-8')

    def test_permanent_stages(self):
        """测试常驻关卡初始化"""
        permanent_stages = self.stage_manager.initialize_permanent_stages()
        self.assertIsNotNone(permanent_stages)
        self.assertGreater(len(permanent_stages), 0)

        # 验证关卡格式
        self.assertIn('display', permanent_stages[0])
        self.assertIn('value', permanent_stages[0])

    def test_is_stage_open(self):
        """测试关卡开放状态判断"""
        # 测试常驻关卡
        ls6_stage = {'display': 'LS-6', 'value': 'LS-6', 'openDays': []}
        self.assertTrue(self.stage_manager.is_stage_open(ls6_stage, 0))  # 应该全天开放

        # 测试资源本
        ce6_stage = {'display': 'CE-6', 'value': 'CE-6', 'openDays': [1, 3, 5, 6]}
        self.assertTrue(self.stage_manager.is_stage_open(ce6_stage, 1))  # 周二开放
        self.assertFalse(self.stage_manager.is_stage_open(ce6_stage, 0))  # 周一不开放

        # 测试活动关卡
        now = datetime.now()
        active_stage = {
            'display': 'Test-1',
            'value': 'Test-1',
            'activity': {
                'utcStartTime': (now - timedelta(days=1)).isoformat(),
                'utcExpireTime': (now + timedelta(days=1)).isoformat()
            }
        }
        self.assertTrue(self.stage_manager.is_stage_open(active_stage, 0))  # 活动期间开放

        # 测试过期活动
        expired_stage = {
            'display': 'Test-2',
            'value': 'Test-2',
            'activity': {
                'utcStartTime': (now - timedelta(days=10)).isoformat(),
                'utcExpireTime': (now - timedelta(days=5)).isoformat()
            }
        }
        self.assertFalse(self.stage_manager.is_stage_open(expired_stage, 0))  # 活动已过期

    def test_get_open_stages(self):
        """测试获取开放关卡列表"""
        # 先确保stage_manager有数据
        self.stage_manager.get_stage_data()

        open_stages = self.stage_manager.get_open_stages(1)  # 周二
        self.assertIsNotNone(open_stages)

        # 检查是否包含周二开放的资源本
        ce6_found = False
        for stage in open_stages:
            if stage['display'] == 'CE-6':
                ce6_found = True
                break

        self.assertTrue(ce6_found, "周二应该开放CE-6")


if __name__ == '__main__':
    unittest.main()