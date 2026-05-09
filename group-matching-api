"""
智能小组匹配系统 - Flask后端
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据文件路径
DATA_FILE = 'participants.json'

# 存储参与者数据
participants = []

def load_data():
    """从文件加载数据"""
    global participants
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                participants = json.load(f)
        except:
            participants = []

def save_data():
    """保存数据到文件"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(participants, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据失败: {e}")

# 启动时加载数据
load_data()

@app.route('/api/participants', methods=['GET'])
def get_participants():
    """获取所有参与者"""
    return jsonify(participants)

@app.route('/api/participants', methods=['POST'])
def add_participant():
    """添加参与者"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        # 验证必填字段
        if not data.get('name', '').strip():
            return jsonify({'error': '姓名不能为空'}), 400
        
        participant = {
            'id': int(data.get('id', 0)) or int(random.random() * 1000000),
            'name': data.get('name', '').strip(),
            'skills': [s.strip() for s in data.get('skills', []) if s.strip()],
            'interests': [i.strip() for i in data.get('interests', []) if i.strip()],
            'level': data.get('level', 'beginner'),
            'created_at': datetime.now().isoformat(),
            'ip': request.remote_addr
        }
        
        # 检查是否已存在
        if any(p['name'].lower() == participant['name'].lower() for p in participants):
            return jsonify({'error': '该姓名已存在'}), 400
        
        participants.append(participant)
        save_data()  # 保存到文件
        
        return jsonify({'success': True, 'participant': participant})
    except Exception as e:
        return jsonify({'error': f'添加失败: {str(e)}'}), 500

@app.route('/api/participants/<int:participant_id>', methods=['DELETE'])
def remove_participant(participant_id):
    """删除参与者"""
    global participants
    participants = [p for p in participants if p.get('id') != participant_id]
    return jsonify({'success': True})

@app.route('/api/participants', methods=['DELETE'])
def clear_participants():
    """清空所有参与者"""
    global participants
    participants = []
    return jsonify({'success': True})

@app.route('/api/match', methods=['POST'])
def match_groups():
    """智能匹配小组"""
    try:
        data = request.json
        participant_list = data.get('participants', [])
        group_count = data.get('groupCount', 2)
        method = data.get('method', 'balanced')
        
        if not participant_list:
            return jsonify({'error': '没有参与者数据'}), 400
        
        if group_count > len(participant_list):
            return jsonify({'error': '小组数量不能超过参与者数量'}), 400
        
        if group_count < 1:
            return jsonify({'error': '小组数量至少为1'}), 400
        
        # 根据方法进行分组
        if method == 'random':
            groups = match_random(participant_list, group_count)
        elif method == 'skill-based':
            groups = match_by_skill(participant_list, group_count)
        elif method == 'level-balanced':
            groups = match_by_level(participant_list, group_count)
        else:
            groups = match_balanced(participant_list, group_count)
        
        # 添加分组时间戳
        result = {
            'groups': groups,
            'method': method,
            'group_count': group_count,
            'total_participants': len(participant_list),
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'分组失败: {str(e)}'}), 500

def match_random(participants_list, group_count):
    """随机分组"""
    shuffled = list(participants_list)
    random.shuffle(shuffled)
    groups = [[] for _ in range(group_count)]
    for i, p in enumerate(shuffled):
        groups[i % group_count].append(p)
    return groups

def match_by_skill(participants_list, group_count):
    """按技能分组 - 尽量让每组技能多样化"""
    # 统计所有技能
    all_skills = {}
    for p in participants_list:
        for skill in p.get('skills', []):
            all_skills[skill] = all_skills.get(skill, 0) + 1
    
    # 按技能数量排序
    sorted_participants = sorted(participants_list, 
                                  key=lambda p: len(p.get('skills', [])), 
                                  reverse=True)
    
    groups = [[] for _ in range(group_count)]
    group_loads = [0] * group_count
    
    for p in sorted_participants:
        # 找到人数最少且技能重复最少的组
        min_load = min(group_loads)
        min_index = group_loads.index(min_load)
        groups[min_index].append(p)
        group_loads[min_index] += 1
    
    return groups

def match_by_level(participants_list, group_count):
    """按水平分组 - 尽量让每组水平均衡"""
    level_weights = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    
    # 按水平排序
    sorted_participants = sorted(
        participants_list,
        key=lambda p: level_weights.get(p.get('level', 'beginner'), 1),
        reverse=True
    )
    
    groups = [[] for _ in range(group_count)]
    group_levels = [0] * group_count
    
    for p in sorted_participants:
        weight = level_weights.get(p.get('level', 'beginner'), 1)
        # 找到水平总和最小的组
        min_level = min(group_levels)
        min_index = group_levels.index(min_level)
        groups[min_index].append(p)
        group_levels[min_index] += weight
    
    return groups

def match_balanced(participants_list, group_count):
    """均衡分组 - 综合考虑技能和水平"""
    level_weights = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
    
    # 计算每个参与者的综合得分
    scored = []
    for p in participants_list:
        score = level_weights.get(p.get('level', 'beginner'), 1) * 10
        score += len(p.get('skills', [])) * 5
        score += len(p.get('interests', [])) * 3
        scored.append((p, score))
    
    # 按得分排序
    scored.sort(key=lambda x: x[1], reverse=True)
    
    groups = [[] for _ in range(group_count)]
    group_scores = [0] * group_count
    
    for p, score in scored:
        # 找到得分最低的组
        min_score = min(group_scores)
        min_index = group_scores.index(min_score)
        groups[min_index].append(p)
        group_scores[min_index] += score
    
    return groups

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    if not participants:
        return jsonify({
            'total_participants': 0,
            'skills_distribution': {},
            'level_distribution': {},
            'interests_distribution': {},
            'recent_registrations': []
        })
    
    # 技能分布
    skills_count = {}
    for p in participants:
        for skill in p.get('skills', []):
            skills_count[skill] = skills_count.get(skill, 0) + 1
    
    # 水平分布
    level_count = {}
    for p in participants:
        level = p.get('level', 'beginner')
        level_count[level] = level_count.get(level, 0) + 1
    
    # 兴趣分布
    interests_count = {}
    for p in participants:
        for interest in p.get('interests', []):
            interests_count[interest] = interests_count.get(interest, 0) + 1
    
    # 最近注册
    recent = sorted(participants, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    return jsonify({
        'total_participants': len(participants),
        'skills_distribution': skills_count,
        'level_distribution': level_count,
        'interests_distribution': interests_count,
        'recent_registrations': recent,
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/export', methods=['GET'])
def export_data():
    """导出数据"""
    format_type = request.args.get('format', 'json')
    
    if format_type == 'csv':
        # 生成CSV格式
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入标题
        writer.writerow(['ID', '姓名', '技能', '兴趣', '水平', '注册时间', 'IP'])
        
        # 写入数据
        for p in participants:
            writer.writerow([
                p.get('id', ''),
                p.get('name', ''),
                ';'.join(p.get('skills', [])),
                ';'.join(p.get('interests', [])),
                p.get('level', ''),
                p.get('created_at', ''),
                p.get('ip', '')
            ])
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': 'attachment; filename=participants.csv'
        }
    
    # 默认JSON格式
    return jsonify({
        'participants': participants,
        'stats': get_stats().get_json(),
        'exported_at': datetime.now().isoformat()
    })

@app.route('/api/groups/history', methods=['GET'])
def get_groups_history():
    """获取历史分组记录"""
    # 这里可以扩展为存储分组历史
    # 目前返回空数组，将来可以保存到文件
    return jsonify({'history': []})

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'participants_count': len(participants),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 智能小组匹配系统后端启动中...")
    print("📍 访问地址: http://localhost:5000")
    print("📍 API文档: http://localhost:5000/health")
    app.run(debug=True, port=5000)
