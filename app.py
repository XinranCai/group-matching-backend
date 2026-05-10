"""
智能小组匹配系统 - Flask后端
完整版：强制每组6-10人，Theme+Topic硬约束，所有字段参与匹配
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)

DATA_FILE = 'participants.json'
participants = []

LEVEL_WEIGHT = {
    '入门': 1,
    '熟练': 2,
    '精通': 3
}

PERSONALITY_ORDER = ['内向', '偏内向', '中性', '偏外向', '外向']


def load_data():
    global participants
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                participants = json.load(f)
        except:
            participants = []


def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(participants, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存失败: {e}")


load_data()


def parse_theme_topic(value):
    if isinstance(value, list):
        return value
    elif isinstance(value, str) and value:
        return [v.strip() for v in value.split(',') if v.strip()]
    else:
        return []


def calculate_match_score(user_a, user_b):
    score = 0
    extra_a = user_a.get('extra', {})
    extra_b = user_b.get('extra', {})
    
    if extra_a.get('deadlineAttitude') == extra_b.get('deadlineAttitude'):
        score += 15
    if extra_a.get('needDivision') == extra_b.get('needDivision'):
        score += 10
    
    pers_a = extra_a.get('personality', '中性')
    pers_b = extra_b.get('personality', '中性')
    if pers_a in PERSONALITY_ORDER and pers_b in PERSONALITY_ORDER:
        diff = abs(PERSONALITY_ORDER.index(pers_a) - PERSONALITY_ORDER.index(pers_b))
        score += diff * 4
    
    skills_a = set(user_a.get('skills', []))
    skills_b = set(user_b.get('skills', []))
    overlap = len(skills_a & skills_b)
    total_skills = len(skills_a) + len(skills_b)
    complement = total_skills - 2 * overlap
    score += complement * 2
    
    styles_a = set(extra_a.get('collabStyles', []))
    styles_b = set(extra_b.get('collabStyles', []))
    common_styles = len(styles_a & styles_b)
    score += common_styles * 3
    
    times_a = set(extra_a.get('timeSlots', []))
    times_b = set(extra_b.get('timeSlots', []))
    common_times = len(times_a & times_b)
    score += common_times * 3
    
    level_a = LEVEL_WEIGHT.get(extra_a.get('mainSkillLevel', '熟练'), 2)
    level_b = LEVEL_WEIGHT.get(extra_b.get('mainSkillLevel', '熟练'), 2)
    level_diff = abs(level_a - level_b)
    score -= level_diff * 2
    
    if extra_a.get('chatBeforeTeam') == extra_b.get('chatBeforeTeam') == '是':
        score += 5
    if extra_a.get('skillPreference') == extra_b.get('skillPreference'):
        score += 5
    
    return max(0, score)


def calculate_group_score(group):
    if len(group) < 2:
        return 0
    total = 0
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            total += calculate_match_score(group[i], group[j])
    return total


def optimize_group_members(members, target_size):
    if not members or len(members) <= target_size:
        return members[:target_size] if members else []
    
    pairs = []
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            pairs.append((calculate_match_score(members[i], members[j]), i, j))
    
    pairs.sort(reverse=True, key=lambda x: x[0])
    
    used = set()
    optimized = []
    for _, i, j in pairs:
        if i in used or j in used:
            continue
        optimized.append(members[i])
        optimized.append(members[j])
        used.add(i)
        used.add(j)
    
    for i in range(len(members)):
        if i not in used:
            optimized.append(members[i])
    
    return optimized[:target_size]


def build_groups(participants_list, min_size=6, max_size=10):
    for p in participants_list:
        extra = p.get('extra', {})
        p['_themes'] = parse_theme_topic(extra.get('theme', ''))
        p['_topics'] = parse_theme_topic(extra.get('topic', ''))
    
    exact_groups = defaultdict(list)
    for p in participants_list:
        themes = p['_themes']
        topics = p['_topics']
        theme_key = themes[0] if themes else 'no_theme'
        topic_key = topics[0] if topics else 'no_topic'
        exact_groups[(theme_key, topic_key)].append(p)
    
    final_groups = []
    unmatched = []
    pending_merge = []
    
    for (theme, topic), members in exact_groups.items():
        size = len(members)
        if theme == 'no_theme' and topic == 'no_topic':
            for p in members:
                unmatched.append({
                    'name': p.get('name', '未知'),
                    'theme': '未选择',
                    'topic': '未选择',
                    'reason': '未选择任何 Theme 和 Topic，无法匹配'
                })
            continue
        
        if size >= min_size:
            num_groups = (size + max_size - 1) // max_size
            group_size = size // num_groups
            remainder = size % num_groups
            start = 0
            for i in range(num_groups):
                current_size = group_size + (1 if i < remainder else 0)
                group_members = members[start:start+current_size]
                optimized = optimize_group_members(group_members, current_size)
                final_groups.append({
                    'theme': theme,
                    'topic': topic,
                    'members': optimized,
                    'size': len(optimized),
                    'is_merged': False
                })
                start += current_size
        elif size >= 2:
            pending_merge.append({
                'theme': theme,
                'topic': topic,
                'members': members,
                'size': size
            })
        else:
            for p in members:
                unmatched.append({
                    'name': p.get('name', '未知'),
                    'theme': theme,
                    'topic': topic,
                    'reason': f'「{theme} - {topic}」方向仅1人，达不到最小组要求'
                })
    
    theme_merge = defaultdict(list)
    for item in pending_merge:
        if item['theme'] != 'no_theme':
            theme_merge[item['theme']].append(item)
    
    for theme, items in theme_merge.items():
        all_members = []
        topics_list = []
        for item in items:
            all_members.extend(item['members'])
            topics_list.append(item['topic'])
        
        total = len(all_members)
        if total >= min_size:
            num_groups = (total + max_size - 1) // max_size
            group_size = total // num_groups
            remainder = total % num_groups
            start = 0
            for i in range(num_groups):
                current_size = group_size + (1 if i < remainder else 0)
                group_members = all_members[start:start+current_size]
                optimized = optimize_group_members(group_members, current_size)
                final_groups.append({
                    'theme': theme,
                    'topic': '合并组（不同Topic）',
                    'members': optimized,
                    'size': len(optimized),
                    'is_merged': True,
                    'original_topics': list(set(topics_list))
                })
                start += current_size
        else:
            for item in items:
                for p in item['members']:
                    unmatched.append({
                        'name': p.get('name', '未知'),
                        'theme': theme,
                        'topic': item['topic'],
                        'reason': f'「{theme}」主题下总人数仅{total}人，达不到最小组要求（{min_size}人）'
                    })
    
    return final_groups, unmatched


@app.route('/api/participants', methods=['GET'])
def get_participants():
    clean = []
    for p in participants:
        p_copy = p.copy()
        p_copy.pop('_themes', None)
        p_copy.pop('_topics', None)
        clean.append(p_copy)
    return jsonify(clean)


@app.route('/api/participants', methods=['POST'])
def add_participant():
    try:
        data = request.json
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        if not data.get('name', '').strip():
            return jsonify({'error': '姓名不能为空'}), 400
        
        student_id = data.get('studentId', '')
        if student_id and any(p.get('studentId') == student_id for p in participants):
            return jsonify({'error': '该学号已存在'}), 400
        
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
    try:
        data = request.json
        participant_list = data.get('participants', [])
        
        if not participant_list:
            return jsonify({'error': '没有参与者数据'}), 400
        
        groups_result, unmatched_users = build_groups(participant_list, min_size=6, max_size=10)
        
        success_groups = []
        for idx, g in enumerate(groups_result):
            group_score = calculate_group_score(g['members'])
            success_groups.append({
                'id': idx + 1,
                'theme': g['theme'],
                'topic': g['topic'],
                'members': [{'name': m.get('name', '未知'), 'skills': m.get('skills', [])} for m in g['members']],
                'size': len(g['members']),
                'internal_score': group_score,
                'is_merged': g.get('is_merged', False)
            })
        
        matched_count = sum([g['size'] for g in success_groups])
        
        return jsonify({
            'success': True,
            'groups': success_groups,
            'unmatched': unmatched_users,
            'total_participants': len(participant_list),
            'matched_count': matched_count,
            'unmatched_count': len(unmatched_users),
            'generated_at': datetime.now().isoformat(),
            'message': f'成功匹配 {matched_count} 人，{len(unmatched_users)} 人暂时无法匹配'
        })
    
    except Exception as e:
        return jsonify({'error': f'分组失败: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not participants:
        return jsonify({
            'total_participants': 0,
            'skills_distribution': {},
            'theme_distribution': {},
            'personality_distribution': {},
            'recent_registrations': []
        })
    
    skills_count = {}
    theme_count = {}
    personality_count = {}
    
    for p in participants:
        for skill in p.get('skills', []):
            skills_count[skill] = skills_count.get(skill, 0) + 1
        
        extra = p.get('extra', {})
        theme = extra.get('theme', 'unknown')
        if isinstance(theme, list):
            for t in theme:
                theme_count[t] = theme_count.get(t, 0) + 1
        else:
            theme_count[theme] = theme_count.get(theme, 0) + 1
        
        personality = extra.get('personality', '中性')
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


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'participants_count': len(participants),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("🚀 智能小组匹配系统后端启动中...")
    print("📍 匹配规则: 每组6-10人，Theme+Topic完全相同优先，同Theme可合并")
    app.run(host='0.0.0.0', port=5000)
