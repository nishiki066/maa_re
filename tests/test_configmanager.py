import unittest
import sys
import os
import json
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config_manager import ConfigManager, SSHConnectionManager

# 跳板机连接参数
JUMPBOX_HOST = "192.168.194.127"
JUMPBOX_USERNAME = "nisiki"
JUMPBOX_PASSWORD = "553216192"

# 目标主机连接参数
TARGET_HOSTS = {
    "cn": {
        "host": "192.168.194.110",
        "username": "ark",
        "password": "553216192",
        "paths": [
            r"C:\Users\zheng\Desktop\maa159b\config\gui.json",
            r"C:\Users\zheng\Desktop\maa177b\config\gui.json"
        ]
    },
    "jp": {
        "host": "192.168.194.128",
        "username": "zjf",
        "password": "553216192",
        "paths": [
            r"C:\Users\zjf\Desktop\maa512\config\gui.json",
            r"C:\Users\zjf\Desktop\maa jp\config\gui.json"
        ]
    }
}


class TestJumpboxConnection(unittest.TestCase):
    def setUp(self):
        self.ssh_manager = SSHConnectionManager()

    def test_jumpbox_connection(self):
        # 测试连接到跳板机
        jumpbox = self.ssh_manager.get_jumpbox_client(
            JUMPBOX_HOST, JUMPBOX_USERNAME, JUMPBOX_PASSWORD
        )
        self.assertIsNotNone(jumpbox, "Failed to connect to jumpbox")

        # 测试通过跳板机执行命令
        print("Testing connection via jumpbox...")
        for target_name, target_info in TARGET_HOSTS.items():
            print(f"Testing connection to {target_name} host...")
            success, result = self.ssh_manager.execute_command_via_jumpbox(
                JUMPBOX_HOST, JUMPBOX_USERNAME, JUMPBOX_PASSWORD,
                target_info["host"], target_info["username"], target_info["password"],
                'echo "Test connection via jumpbox"'
            )
            print(f"Connection result: {success}, output: {result}")
            self.assertTrue(success, f"Failed to connect to {target_name} host via jumpbox")

    def tearDown(self):
        self.ssh_manager.close_all()


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.manager = ConfigManager()

        # 添加测试实例
        self.cn_instance_name = "cn_maa159"
        self.jp_instance_name = "jp_maa512"

        # 添加CN实例
        self.cn_instance = self.manager.add_instance(
            self.cn_instance_name,
            TARGET_HOSTS["cn"]["host"],
            TARGET_HOSTS["cn"]["username"],
            TARGET_HOSTS["cn"]["password"],
            TARGET_HOSTS["cn"]["paths"][0],
            JUMPBOX_HOST, JUMPBOX_USERNAME, JUMPBOX_PASSWORD
        )

        # 添加JP实例
        self.jp_instance = self.manager.add_instance(
            self.jp_instance_name,
            TARGET_HOSTS["jp"]["host"],
            TARGET_HOSTS["jp"]["username"],
            TARGET_HOSTS["jp"]["password"],
            TARGET_HOSTS["jp"]["paths"][0],
            JUMPBOX_HOST, JUMPBOX_USERNAME, JUMPBOX_PASSWORD
        )

    def test_refresh_instance(self):
        # 测试刷新实例配置
        print(f"\nTesting refresh for {self.cn_instance_name}...")
        cn_success = self.manager.refresh_instance(self.cn_instance_name)
        print(f"CN instance online: {self.cn_instance.online}, refresh result: {cn_success}")

        print(f"\nTesting refresh for {self.jp_instance_name}...")
        jp_success = self.manager.refresh_instance(self.jp_instance_name)
        print(f"JP instance online: {self.jp_instance.online}, refresh result: {jp_success}")

        # 至少有一个实例应该成功
        self.assertTrue(cn_success or jp_success, "Both instances failed to refresh")

    def tearDown(self):
        self.manager.close()


if __name__ == "__main__":
    unittest.main()