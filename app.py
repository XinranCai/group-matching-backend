"""
智能小组匹配系统 - Flask后端
完整版：强制每组6-10人，Theme+Topic硬约束，所有字段参与匹配
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import random
import json
import os
import csv
import io
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据文件路径
DATA_FILE = 'participants.json'
MATCH_HISTORY_FILE = 'match_history.json'

# 存储参与者数据
participants = []
match_history = []

# 水平权重映射
LEVEL_WEIGHT = {
    '入门': 1,
    '熟练': 2,
    '精通': 3
}

# 性格顺序映射（用于计算差异）
PERSONALITY_ORDER = ['内向', '偏内向', '中性', '偏外向', '外向']


def load_data():
    """从文件加载数据"""
    global participants, match_history
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                participants = json.load(f)
        except:
            participants = []
    if os.path.exists(MATCH_HISTORY_FILE):
        try:
            with open(MATCH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                match_history = json.load(f)
        except:
            match_history = []


def save_data():
    """保存数据到文件"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(participants, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存数据失败: {e}")


def save_match_history():
    """保存匹配历史"""
    try:
        with open(MATCH_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(match_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存匹配历史失败: {e}")


# 启动时加载数据
load_data()


def parse_theme_topic(value):
    """解析前端传来的多选 Theme/Topic（可能是字符串或数组）"""
    if isinstance(value, list):
        return value
    elif isinstance(value, str) and value:
        return [v.strip() for v in value.split(',') if v.strip()]
    else:
        return []


def themes_match(theme_list_a, theme_list_b):
    """检查两个用户的 Theme 是否有交集"""
    if not theme_list_a or not theme_list_b:
        return False
    return len(set(theme_list_a) & set(theme_list_b)) > 0


def topics_match(topic_list_a, topic_list_b):
    """检查两个用户的 Topic 是否有交集"""
    if not topic_list_a or not topic_list_b:
        return False
    return len(set(topic_list_a) & set(topic_list_b)) > 0


def calculate_match_score_detail(user_a, user_b):
    """
    计算两个用户之间的匹配分（返回详细分数）
    分数越高，越适合分在同一组
    """
    result = {
        'ddl': 0,
        'division': 0,
        'personality': 0,
        'skill': 0,
        'collab': 0,
        'time': 0,
        'level_penalty': 0,
        'chat': 0,
        'skill_pref': 0,
        'total': 0
    }
    
    extra_a = user_a.get('extra', {})
    extra_b = user_b.get('extra', {})
    
    # P1: DDL态度 (权重 15)
    if extra_a.get('deadlineAttitude') == extra_b.get('deadlineAttitude'):
        result['ddl'] = 15
    
    # P1: 分工需求 (权重 10)
    if extra_a.get('needDivision') == extra_b.get('needDivision'):
        result['division'] = 10
    
    # P2: 性格多样性 (权重 20) - 性格差异越大分越高
    pers_a = extra_a.get('personality', '中性')
    pers_b = extra_b.get('personality', '中性')
    if pers_a in PERSONALITY_ORDER and pers_b in PERSONALITY_ORDER:
        diff = abs(PERSONALITY_ORDER.index(pers_a) - PERSONALITY_ORDER.index(pers_b))
        result['personality'] = diff * 4  # 最大16分
    
    # P3: 技能互补 (权重 20) - 技能重叠越少分越高
    skills_a = set(user_a.get('skills', []))
    skills_b = set(user_b.get('skills', []))
    overlap = len(skills_a & skills_b)
    total_skills = len(skills_a) + len(skills_b)
    complement = total_skills - 2 * overlap
    result['skill'] = complement * 2  # 最大约20分
    
    # P4: 协作风格匹配 (权重 15)
    styles_a = set(extra_a.get('collabStyles', []))
    styles_b = set(extra_b.get('collabStyles', []))
    common_styles = len(styles_a & styles_b)
    result['collab'] = common_styles * 3
    
    # P5: 时间可用性重叠 (权重 10)
    times_a = set(extra_a.get('timeSlots', []))
    times_b = set(extra_b.get('timeSlots', []))
    common_times = len(times_a & times_b)
    result['time'] = common_times * 3
    
    # P6: 技能水平差距 (权重 -5，差距大扣分)
    level_a = LEVEL_WEIGHT.get(extra_a.get('mainSkillLevel', '熟练'), 2)
    level_b = LEVEL_WEIGHT.get(extra_b.get('mainSkillLevel', '熟练'), 2)
    level_diff = abs(level_a - level_b)
    result['level_penalty'] = -level_diff * 2
    
    # P7: 私聊意愿 (权重 5)
    if extra_a.get('chatBeforeTeam') == extra_b.get('chatBeforeTeam') == '是':
        result['chat'] = 5
    
    # P8: 技能偏好 (权重 5)
    if extra_a.get('skillPreference') == extra_b.get('skillPreference'):
        result['skill_pref'] = 5
    
    result['total'] = sum([
        result['ddl'], result['division'], result['personality'],
        result['skill'], result['collab'], result['time'],
        result['level_penalty'], result['chat'], result['skill_pref']
    ])
    result['total'] = max(0, result['total'])
    
    return result


def calculate_match_score(user_a, user_b):
    """计算两个用户之间的匹配分（返回总分）"""
    return calculate_match_score_detail(user_a, user_b)['total']


def calculate_group_internal_score_detail(group):
    """
    计算组内和谐度总分及详细分数
    返回总分和每对成员的详细分数
    """
    if len(group) < 2:
        return {'total': 0, 'pairs': []}
    
    pairs_detail = []
    total_score = 0
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            pair_score = calculate_match_score_detail(group[i], group[j])
            pairs_detail.append({
                'user_a': group[i].get('name', '未知'),
                'user_b': group[j].get('name', '未知'),
                'scores': pair_score
            })
            total_score += pair_score['total']
    return {'total': total_score, 'pairs': pairs_detail}


def greedy_match_within_group(candidates, target_size):
    """
    在候选列表中贪心分组
    返回：分组列表
    """
    if not candidates:
        return []
    
    # 计算所有配对分数
    pairs = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            score = calculate_match_score(candidates[i], candidates[j])
            pairs.append((score, i, j))
    
    # 按分数降序排序
    pairs.sort(reverse=True, key=lambda x: x[0])
    
    used = set()
    groups = []
    
    # 贪心配对
    for score, i, j in pairs:
        if i in used or j in used:
            continue
        groups.append([candidates[i], candidates[j]])
        used.add(i)
        used.add(j)
    
    # 处理剩余未配对的
    remaining = [candidates[i] for i in range(len(candidates)) if i not in used]
    for r in remaining:
        best_group = None
        best_score = -1
        for g in groups:
            if len(g) < target_size:
                temp_score = 0
                for member in g:
                    temp_score += calculate_match_score(r, member)
                if temp_score > best_score:
                    best_score = temp_score
                    best_group = g
        if best_group:
            best_group.append(r)
        else:
            groups.append([r])
    
    # 调整每组到目标大小
    optimized_groups = []
    for g in groups:
        if len(g) >= target_size - 1:
            optimized_groups.append(g[:target_size])
            if len(g) > target_size:
                remaining_people = g[target_size:]
                for p in remaining_people:
                    added = False
                    for og in optimized_groups:
                        if len(og) < target_size + 1:
                            og.append(p)
                            added = True
                            break
                    if not added:
                        optimized_groups.append([p])
        else:
            optimized_groups.append(g)
    
    return optimized_groups


def build_groups_by_theme_topic(participants_list, min_size=6, max_size=10):
    """
    核心分组算法：
    1. 按 Theme 和 Topic 的语义相关性分组（可合并相同 Theme 或相同 Topic）
    2. 每组人数控制在 min_size 到 max_size 之间
    3. 人数不足的合并到同 Theme 或同 Topic 的其他组
    4. 仍然不足的标记为无法匹配
    """
    
    # 1. 计算每个用户的 Theme 和 Topic 列表
    for p in participants_list:
        extra = p.get('extra', {})
        theme_str = extra.get('theme', '')
        topic_str = extra.get('topic', '')
        p['_themes'] = parse_theme_topic(theme_str)
        p['_topics'] = parse_theme_topic(topic_str)
    
    # 2. 构建分组（使用并查集思想，有公共 Theme 或公共 Topic 的人可以合并）
    groups_dict = {}  # key: 组标识，value: 成员列表
    group_theme_topic = {}  # 组的标识（主 Theme+Topic）
    
    for p in participants_list:
        p_themes = set(p['_themes'])
        p_topics = set(p['_topics'])
        
        # 找是否有已有组与当前用户匹配
        matched_group = None
        for g_id, g_members in groups_dict.items():
            # 检查组内成员的 Theme 和 Topic
            for m in g_members:
                m_themes = set(m['_themes'])
                m_topics = set(m['_topics'])
                if p_themes & m_themes or p_topics & m_topics:
                    matched_group = g_id
                    break
            if matched_group:
                break
        
        if matched_group:
            groups_dict[matched_group].append(p)
        else:
            new_id = len(groups_dict)
            groups_dict[new_id] = [p]
            # 记录该组的代表性 Theme 和 Topic
            if p_themes:
                group_theme_topic[new_id] = (list(p_themes)[0], list(p_topics)[0] if p_topics else '未指定')
            else:
                group_theme_topic[new_id] = ('未指定', '未指定')
    
    # 3. 处理每组人数
    final_groups = []
    for g_id, members in groups_dict.items():
        size = len(members)
        theme, topic = group_theme_topic[g_id]
        
        if size >= min_size:
            # 人数足够，分成多个小组
            num_groups = (size + max_size - 1) // max_size
            group_size = size // num_groups
            remainder = size % num_groups
            
            start = 0
            for i in range(num_groups):
                current_size = group_size + (1 if i < remainder else 0)
                group_members = members[start:start+current_size]
                optimized = greedy_match_within_group(group_members, current_size)
                for g in optimized:
                    final_groups.append({
                        'theme': theme,
                        'topic': topic,
                        'members': g,
                        'size': len(g),
                        'is_merged': False
                    })
                start += current_size
        elif size >= 2:
            # 人数不足，直接成组（标记为合并组）
            # 在组内进行优化排序
            optimized = greedy_match_within_group(members, min_size)
            for g in optimized:
                final_groups.append({
                    'theme': theme,
                    'topic': topic + '（人数不足）',
                    'members': g,
                    'size': len(g),
                    'is_merged': True,
                    'unmatched': True,
                    'reason': f'该方向共{size}人，达不到最小组要求（{min_size}人）'
                })
        else:
            # 只有1人
            for p in members:
                final_groups.append({
                    'theme': theme,
                    'topic': topic,
                    'members': [p],
                    'size': 1,
                    'unmatched': True,
                    'reason': f'「{theme} - {topic}」方向仅1人，达不到最小组要求'
                })
    
    return final_groups


@app.route('/api/participants', methods=['GET'])
def get_participants():
    """获取所有参与者"""
    # 移除内部字段
    clean_participants = []
    for p in participants:
        p_copy = p.copy()
        p_copy.pop('_themes', None)
        p_copy.pop('_topics', None)
        clean_participants.append(p_copy)
    return jsonify(clean_participants)


@app.route('/api/participants', methods=['POST'])
def add_participant():
    """添加参与者"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        if not data.get('name', '').strip():
            return jsonify({'error': '姓名不能为空'}), 400
        
        student_id = data.get('studentId', '')
        if student_id and any(p.get('studentId') == student_id for p in participants):
            return jsonify({'error': '该学号已存在'}), 400
        
        # 处理多选 Theme/Topic
        theme = data.get('theme', '')
        topic = data.get('topic', '')
        
        participant = {
            'id': int(data.get('id', 0)) or int(random.random() * 1000000),
            'studentId': data.get('studentId', ''),
            'name': data.get('name', '').strip(),
            'skills': data.get('skills', []),
            'level': data.get('level', 'intermediate'),
            'created_at': datetime.now().isoformat(),
            'extra': {
                'theme': theme if isinstance(theme, list) else theme,
                'topic': topic if isinstance(topic, list) else topic,
                'mbti': data.get('mbti', ''),
                'personality': data.get('personality', '中性'),
                'teamPersonality': data.get('teamPersonality', '多样化'),
                'collabStyles': data.get('collabStyles', []),
                'deadlineAttitude': data.get('deadlineAttitude', '灵活按时'),
                'needDivision': data.get('needDivision', '是'),
                'timeSlots': data.get('timeSlots', []),
                'skillPreference': data.get('skillPreference', '互补'),
                'filterWay': data.get('filterWay', '标签勾选'),
                'excludeNeed': data.get('excludeNeed', '偶尔需要'),
                'chatBeforeTeam': data.get('chatBeforeTeam', '是'),
                'customPreference': data.get('customPreference', ''),
                'additionalNote': data.get('additionalNote', ''),
                'mainSkillLevel': data.get('mainSkillLevel', '熟练'),
                'secSkillLevel': data.get('secSkillLevel', '熟练')
            }
        }
        
        participants.append(participant)
        save_data()
        
        return jsonify({'success': True, 'participant': participant})
    except Exception as e:
        return jsonify({'error': f'添加失败: {str(e)}'}), 500


@app.route('/api/match', methods=['POST'])
def match_groups():
    """
    智能匹配小组
    强制每组6-10人
    """
    try:
        data = request.json
        participant_list = data.get('participants', [])
        
        if not participant_list:
            return jsonify({'error': '没有参与者数据'}), 400
        
        # 使用分组算法
        groups_result = build_groups_by_theme_topic(participant_list, min_size=6, max_size=10)
        
        # 分离成功组和未匹配组
        success_groups = []
        unmatched_users = []
        
        for g in groups_result:
            if g.get('unmatched'):
                for member in g['members']:
                    unmatched_users.append({
                        'name': member.get('name', '未知'),
                        'theme': g['theme'],
                        'topic': g['topic'],
                        'reason': g.get('reason', '人数不足无法成组')
                    })
            else:
                # 计算组内详细分数
                score_detail = calculate_group_internal_score_detail(g['members'])
                success_groups.append({
                    'id': len(success_groups) + 1,
                    'theme': g['theme'],
                    'topic': g['topic'],
                    'members': [{'name': m.get('name', '未知'), 'skills': m.get('skills', [])} for m in g['members']],
                    'size': len(g['members']),
                    'internal_score': score_detail['total'],
                    'score_pairs': score_detail['pairs'],  # 新增：每对成员详细分数
                    'is_merged': g.get('is_merged', False)
                })
        
        matched_count = sum([g['size'] for g in success_groups])
        unmatched_count = len(unmatched_users)
        
        # 保存匹配历史
        match_record = {
            'timestamp': datetime.now().isoformat(),
            'total_participants': len(participant_list),
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'groups': success_groups,
            'unmatched': unmatched_users
        }
        match_history.append(match_record)
        save_match_history()
        
        result = {
            'success': True,
            'groups': success_groups,
            'unmatched': unmatched_users,
            'total_participants': len(participant_list),
            'matched_count': matched_count,
            'unmatched_count': unmatched_count,
            'generated_at': datetime.now().isoformat(),
            'message': f'成功匹配 {matched_count} 人，{unmatched_count} 人暂时无法匹配'  # 修复：正确计算人数
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'分组失败: {str(e)}'}), 500


@app.route('/api/match/export', methods=['POST'])
def export_match_result():
    """导出匹配结果为 CSV"""
    try:
        data = request.json
        groups = data.get('groups', [])
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['组号', 'Theme', 'Topic', '成员姓名', '技能', '组内匹配分'])
        
        for group in groups:
            group_id = group.get('id', '')
            theme = group.get('theme', '')
            topic = group.get('topic', '')
            score = group.get('internal_score', 0)
            for member in group.get('members', []):
                writer.writerow([
                    group_id, theme, topic,
                    member.get('name', ''),
                    ';'.join(member.get('skills', [])),
                    score
                ])
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': 'attachment; filename=match_result.csv'
        }
    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """管理员：获取所有用户详情"""
    clean_users = []
    for p in participants:
        clean_users.append({
            'id': p.get('id'),
            'studentId': p.get('studentId'),
            'name': p.get('name'),
            'skills': p.get('skills', []),
            'level': p.get('level'),
            'extra': p.get('extra', {}),
            'created_at': p.get('created_at')
        })
    return jsonify({
        'total': len(clean_users),
        'users': clean_users
    })


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    """管理员：删除指定用户"""
    global participants
    user = next((p for p in participants if p.get('id') == user_id), None)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    participants = [p for p in participants if p.get('id') != user_id]
    save_data()
    return jsonify({'success': True, 'message': f'已删除用户 {user.get("name")}'})


@app.route('/api/admin/clear', methods=['DELETE'])
def admin_clear_all():
    """管理员：清空所有用户数据"""
    global participants
    participants = []
    save_data()
    return jsonify({'success': True, 'message': '已清空所有用户数据'})


@app.route('/api/admin/match-history', methods=['GET'])
def admin_get_match_history():
    """管理员：获取匹配历史"""
    return jsonify({
        'total': len(match_history),
        'history': match_history[-10:]  # 最近10次
    })


@app.route('/api/participants/<int:participant_id>', methods=['DELETE'])
def remove_participant(participant_id):
    """删除参与者"""
    global participants
    participants = [p for p in participants if p.get('id') != participant_id]
    save_data()
    return jsonify({'success': True})


@app.route('/api/participants', methods=['DELETE'])
def clear_participants():
    """清空所有参与者"""
    global participants
    participants = []
    save_data()
    return jsonify({'success': True})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    if not participants:
        return jsonify({
            'total_participants': 0,
            'skills_distribution': {},
            'level_distribution': {},
            'theme_distribution': {},
            'personality_distribution': {},
            'recent_registrations': []
        })
    
    skills_count = {}
    for p in participants:
        for skill in p.get('skills', []):
            skills_count[skill] = skills_count.get(skill, 0) + 1
    
    theme_count = {}
    for p in participants:
        extra = p.get('extra', {})
        theme = extra.get('theme', 'unknown')
        if isinstance(theme, list):
            for t in theme:
                theme_count[t] = theme_count.get(t, 0) + 1
        else:
            theme_count[theme] = theme_count.get(theme, 0) + 1
    
    personality_count = {}
    for p in participants:
        personality = p.get('extra', {}).get('personality', '中性')
        personality_count[personality] = personality_count.get(personality, 0) + 1
    
    recent = sorted(participants, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
    return jsonify({
        'total_participants': len(participants),
        'skills_distribution': skills_count,
        'theme_distribution': theme_count,
        'personality_distribution': personality_count,
        'recent_registrations': recent,
        'generated_at': datetime.now().isoformat()
    })


@app.route('/api/export', methods=['GET'])
def export_data():
    """导出数据为 CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['姓名', '学号', '技能', '性格', 'Theme', 'Topic', 'DDL态度', '分工需求', '注册时间'])
    
    for p in participants:
        extra = p.get('extra', {})
        theme = extra.get('theme', '')
        if isinstance(theme, list):
            theme = ';'.join(theme)
        topic = extra.get('topic', '')
        if isinstance(topic, list):
            topic = ';'.join(topic)
        
        writer.writerow([
            p.get('name', ''),
            p.get('studentId', ''),
            ';'.join(p.get('skills', [])),
            extra.get('personality', ''),
            theme,
            topic,
            extra.get('deadlineAttitude', ''),
            extra.get('needDivision', ''),
            p.get('created_at', '')
        ])
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename=participants.csv'
    }


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
    print("📍 匹配规则: 每组6-10人，Theme/Topic 语义匹配")
    app.run(debug=True, port=5000)
