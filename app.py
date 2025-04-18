from flask import Flask, jsonify
from stage_manager import StageDataManager

app = Flask(__name__)
stage_manager = StageDataManager()

@app.route('/api/stages', methods=['GET'])
def get_stages():
    """获取所有关卡数据"""
    stage_data = stage_manager.get_stage_data()
    return jsonify(stage_data)

@app.route('/api/stages/refresh', methods=['GET'])
def refresh_stages():
    """强制刷新关卡数据"""
    stage_data = stage_manager.get_stage_data(force_refresh=True)
    return jsonify({'success': True, 'data': stage_data})

@app.route('/api/stages/open', methods=['GET'])
def get_open_stages():
    """获取当前开放的关卡"""
    open_stages = stage_manager.get_open_stages()
    return jsonify(open_stages)

if __name__ == '__main__':
    app.run(debug=True, port=5000)