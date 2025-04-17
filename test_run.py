from stage_manager import StageDataManager
import json


def main():
    # 初始化StageDataManager
    manager = StageDataManager()

    # 获取关卡数据
    print("获取关卡数据...")
    stage_data = manager.get_stage_data()

    # 输出基本信息
    print(f"常驻关卡数量: {len(stage_data.get('permanent', []))}")
    print(f"活动关卡数量: {len(stage_data.get('activity', []))}")

    # 获取当前开放的关卡
    open_stages = manager.get_open_stages()
    print(f"\n当前开放关卡数量: {len(open_stages)}")
    print("当前开放关卡列表:")
    for stage in open_stages:
        print(f"- {stage['display']} ({stage['value']})")

    # 输出活动关卡详情
    print("\n活动关卡详情:")
    for stage in stage_data.get('activity', []):
        activity = stage.get('activity', {})
        print(f"- {stage['display']}: {activity.get('stageName', '未知')} ({stage.get('drop', '无掉落信息')})")

        if 'utcExpireTime' in activity:
            expire_time = activity['utcExpireTime']
            print(f"  过期时间: {expire_time}")


if __name__ == "__main__":
    main()