<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>西浦组队通 - 智能小组匹配</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: linear-gradient(135deg, #e8f4f8 0%, #f0e6f5 100%); font-family: 'Inter', sans-serif; padding: 20px; color: #2c3e50; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 24px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.05); }
        h1 { font-size: 2rem; margin-bottom: 10px; background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec489a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        h2 { font-size: 1.4rem; margin-bottom: 16px; color: #3b82f6; border-left: 4px solid #8b5cf6; padding-left: 12px; }
        .subtitle { color: #6c757d; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 8px; color: #2c3e50; font-size: 0.9rem; }
        input, select, textarea { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 16px; font-size: 16px; transition: all 0.2s; background: #fafcff; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #8b5cf6; box-shadow: 0 0 0 3px rgba(139,92,246,0.1); }
        button { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border: none; padding: 12px 24px; border-radius: 40px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59,130,246,0.3); }
        .btn-submit { width: 100%; padding: 14px; font-size: 1rem; margin-top: 10px; background: linear-gradient(135deg, #10b981, #3b82f6); }
        .btn-accent { background: linear-gradient(135deg, #f59e0b, #ef4444); }
        .btn-accent:hover { box-shadow: 0 10px 20px rgba(245,158,11,0.3); }
        .section-card { background: #ffffff; border-radius: 20px; padding: 20px; margin-bottom: 24px; border: 1px solid #eef2f8; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
        .section-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; color: #3b82f6; display: flex; align-items: center; gap: 10px; }
        .section-title i { color: #8b5cf6; font-size: 1.3rem; }
        .skill-tag, .theme-tag, .topic-tag { display: inline-block; background: #f1f5f9; padding: 8px 18px; border-radius: 40px; margin: 4px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; border: 1px solid #e2e8f0; color: #334155; }
        .skill-tag.selected, .theme-tag.selected, .topic-tag.selected { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border-color: transparent; }
        .tags-group { margin: 12px 0; }
        .chat-messages { background: #f8fafc; border-radius: 16px; border: 1px solid #e2e8f0; padding: 14px; max-height: 220px; overflow-y: auto; margin-bottom: 12px; }
        .chat-message { background: #ffffff; border-radius: 16px; padding: 10px 14px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-size: 0.95rem; }
        .chat-message.chat-system { background: #eff6ff; color: #1e40af; border-left: 3px solid #3b82f6; }
        .two-columns { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 0.5rem; }
        .col { flex: 1; min-width: 180px; }
        .option-group { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
        .option-item { display: flex; align-items: center; gap: 8px; background: #f8fafc; padding: 8px 16px; border-radius: 40px; border: 1px solid #e2e8f0; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
        .option-item:hover { background: #eff6ff; border-color: #3b82f6; }
        .option-item input { width: auto; margin-right: 4px; }
        .nav-tabs { display: flex; justify-content: center; gap: 12px; margin-bottom: 30px; flex-wrap: wrap; }
        .nav-tab { padding: 10px 24px; cursor: pointer; border-radius: 40px; font-weight: 600; background: white; color: #3b82f6; transition: all 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        .nav-tab.active { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border-color: transparent; }
        .page-section { display: none; }
        .page-section.active { display: block; }
        .privacy-note { text-align: center; font-size: 0.7rem; color: #94a3b8; margin-top: 18px; }
        hr { margin: 16px 0; border-color: #e2e8f0; }
        .range-slider { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
        .range-slider input { flex: 1; }
        .range-value { background: #3b82f6; color: white; padding: 4px 12px; border-radius: 30px; font-size: 0.9rem; font-weight: 600; }
        @media (max-width: 640px) { body { padding: 12px; } .card { padding: 20px; } .nav-tab { padding: 6px 16px; font-size: 14px; } }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h1>🎓 西浦组队通</h1>
        <p class="subtitle">XJTLU TeamUp - 智能小组匹配系统</p>
    </div>

    <div class="nav-tabs">
        <div class="nav-tab active" data-page="profile">📝 完善资料</div>
        <div class="nav-tab" data-page="match">🎯 智能匹配</div>
        <div class="nav-tab" data-page="members">👥 成员列表</div>
    </div>

    <!-- 完善资料页面 -->
    <div class="page-section active" id="profile-page">
        <div class="card">
            <h2>📋 完善个人资料</h2>
            <div id="profileMsg"></div>

            <!-- 基本信息 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-id-badge"></i> 基本信息</div>
                <div class="form-group">
                    <label>学号 *</label>
                    <input type="text" id="studentId" placeholder="请输入学号">
                </div>
                <div class="form-group">
                    <label>姓名 *</label>
                    <input type="text" id="name" placeholder="请输入姓名">
                </div>
                <div class="form-group">
                    <label>MBTI（可选）</label>
                    <input type="text" id="mbti" placeholder="例如 ENTP">
                </div>
            </div>

            <!-- 项目方向（多选） -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-compass"></i> 项目方向（可多选）</div>
                <div class="tags-group" id="themesContainer">
                    <span class="theme-tag" data-theme="theme-a">Theme A: CS & Software</span>
                    <span class="theme-tag" data-theme="theme-b">Theme B: Electronic Eng</span>
                    <span class="theme-tag" data-theme="theme-c">Theme C: Architecture</span>
                    <span class="theme-tag" data-theme="theme-d">Theme D: Health & Bio</span>
                    <span class="theme-tag" data-theme="theme-e">Theme E: Business & Econ</span>
                    <span class="theme-tag" data-theme="theme-f">Theme F: Digital Media</span>
                    <span class="theme-tag" data-theme="theme-g">Theme G: Humanities</span>
                    <span class="theme-tag" data-theme="theme-h">Theme H: Academic</span>
                </div>
                <div style="margin-top: 12px;" id="topicsContainer">
                    <div style="font-size: 0.8rem; color: #64748b;">💡 请先选择 Theme，再选择 Topic</div>
                </div>
            </div>

            <!-- 技能画像 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-code"></i> 技能画像</div>
                <div class="tags-group" id="skillsContainer">
                    <span class="skill-tag" data-skill="策划">📋 策划</span>
                    <span class="skill-tag" data-skill="写作">✍️ 写作</span>
                    <span class="skill-tag" data-skill="设计">🎨 设计</span>
                    <span class="skill-tag" data-skill="编程">💻 编程</span>
                    <span class="skill-tag" data-skill="数据分析">📊 数据分析</span>
                    <span class="skill-tag" data-skill="执行">⚡ 执行</span>
                    <span class="skill-tag" data-skill="演讲">🎤 演讲</span>
                    <span class="skill-tag" data-skill="文献检索">📚 文献检索</span>
                    <span class="skill-tag" data-skill="排版">📐 排版</span>
                    <span class="skill-tag" data-skill="统筹">🗂️ 统筹</span>
                </div>
                <div class="two-columns">
                    <div class="col"><label>首选技能熟练度</label><select id="mainSkillLevel"><option>入门</option><option selected>熟练</option><option>精通</option></select></div>
                    <div class="col"><label>次选技能熟练度</label><select id="secSkillLevel"><option>入门</option><option selected>熟练</option><option>精通</option></select></div>
                </div>
            </div>

            <!-- 性格 & 协作偏好 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-smile"></i> 性格 & 协作偏好</div>
                <div class="two-columns">
                    <div class="col"><label>性格自评</label><div class="option-group"><label class="option-item"><input type="radio" name="personality" value="内向">🌙 内向</label><label class="option-item"><input type="radio" name="personality" value="偏内向">🌓 偏内向</label><label class="option-item"><input type="radio" name="personality" value="中性" checked>⚖️ 中性</label><label class="option-item"><input type="radio" name="personality" value="偏外向">🌤️ 偏外向</label><label class="option-item"><input type="radio" name="personality" value="外向">☀️ 外向</label></div></div>
                    <div class="col"><label>协作风格</label><div class="option-group"><label class="option-item"><input type="checkbox" name="collabStyle" value="明确分工">📅 明确分工</label><label class="option-item"><input type="checkbox" name="collabStyle" value="自由协作">🎈 自由协作</label><label class="option-item"><input type="checkbox" name="collabStyle" value="定期讨论">💬 定期讨论</label><label class="option-item"><input type="checkbox" name="collabStyle" value="最后冲刺">🚀 最后冲刺</label></div></div>
                </div>
                <div style="margin-top: 12px;"><label>希望的队友性格分布</label><div class="option-group"><label class="option-item"><input type="radio" name="teamPersonality" value="全部内向">🌙 全部内向</label><label class="option-item"><input type="radio" name="teamPersonality" value="大多外向">☀️ 大多外向</label><label class="option-item"><input type="radio" name="teamPersonality" value="多样化" checked>🌈 多样化</label></div></div>
            </div>

            <!-- 工作效率偏好 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-clock"></i> 工作效率偏好</div>
                <div class="two-columns">
                    <div class="col"><label>对DDL的态度</label><div class="option-group"><label class="option-item"><input type="radio" name="deadlineAttitude" value="严格遵守" checked>⏰ 严格遵守</label><label class="option-item"><input type="radio" name="deadlineAttitude" value="灵活按时">✅ 灵活按时</label><label class="option-item"><input type="radio" name="deadlineAttitude" value="可接受延期">📅 可接受延期</label></div></div>
                    <div class="col"><label>是否需要明确分工</label><div class="option-group"><label class="option-item"><input type="radio" name="needDivision" value="是" checked>📋 是，需要</label><label class="option-item"><input type="radio" name="needDivision" value="否">🎯 灵活即可</label></div></div>
                </div>
                <div style="margin-top: 12px;"><label>可用讨论时间 (多选)</label><div class="option-group"><label class="option-item"><input type="checkbox" name="timeSlots" value="工作日晚间">🌙 工作日晚间</label><label class="option-item"><input type="checkbox" name="timeSlots" value="周末全天">☀️ 周末全天</label><label class="option-item"><input type="checkbox" name="timeSlots" value="随机/灵活">🔄 随机/灵活</label></div></div>
            </div>

            <!-- 组队偏好 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-magnet"></i> 组队偏好</div>
                <div class="two-columns">
                    <div class="col"><label>技能组队倾向</label><div class="option-group"><label class="option-item"><input type="radio" name="skillPreference" value="互补" checked>🔧 技能互补</label><label class="option-item"><input type="radio" name="skillPreference" value="相似">🎯 技能相似</label></div></div>
                    <div class="col"><label>匹配后私聊</label><div class="option-group"><label class="option-item"><input type="radio" name="chatBeforeTeam" value="是" checked>💬 是，先沟通</label><label class="option-item"><input type="radio" name="chatBeforeTeam" value="否">🤝 直接组队</label></div></div>
                </div>
            </div>

            <!-- 预组队商议聊天 -->
            <div id="chat-discussion-section" class="section-card">
                <div class="section-title"><i class="fas fa-comments"></i> 预组队商议聊天</div>
                <div id="chatMessages" class="chat-messages">
                    <div class="chat-message chat-system"><strong>💡 系统：</strong> 这里会保存你本次预组队讨论的关键内容，方便后续匹配和沟通。</div>
                </div>
                <textarea id="chat-input" rows="4" placeholder="例如：希望先确认角色分工、讨论时间安排、确定项目风格" style="width:100%; border-radius: 16px; border:1px solid #e2e8f0; padding: 12px; font-family: inherit;"></textarea>
                <button type="button" id="chat-send-btn" style="margin-top: 12px; width:auto; padding: 10px 18px; background: linear-gradient(135deg, #10b981, #3b82f6);">💾 保存商议内容</button>
            </div>

            <!-- 补充信息 -->
            <div class="section-card">
                <div class="section-title"><i class="fas fa-pen-fancy"></i> 补充信息</div>
                <div class="form-group"><textarea id="additionalNote" rows="3" placeholder="其他想补充的信息..." style="background:#fafcff;"></textarea></div>
            </div>

            <button class="btn-submit" id="submitBtn">🚀 生成匹配画像 & 进入匹配池</button>
            <div class="privacy-note"><i class="fas fa-shield-alt"></i> 信息仅用于小组匹配，不会公开</div>
        </div>
    </div>

    <!-- 智能匹配页面 -->
    <div class="page-section" id="match-page">
        <div class="card">
            <h2>🎯 智能匹配</h2>
            <div class="form-group">
                <label>每组人数范围</label>
                <div class="range-slider">
                    <span>6人</span>
                    <input type="range" id="groupSizeRange" min="6" max="10" value="8" step="1">
                    <span class="range-value" id="groupSizeValue">8人</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 8px;">系统将尽量按此人数分组，实际可能因总人数略有浮动</div>
            </div>
            <button id="matchBtn" class="btn-accent">✨ 开始智能匹配</button>
            <div id="matchResult" style="margin-top: 20px;"></div>
        </div>
    </div>

    <!-- 成员列表页面 -->
    <div class="page-section" id="members-page">
        <div class="card">
            <h2>👥 匹配池成员</h2>
            <button id="refreshBtn" style="margin-bottom: 16px; background: linear-gradient(135deg, #8b5cf6, #ec489a);">🔄 刷新列表</button>
            <div id="participantsList">加载中...</div>
        </div>
    </div>
</div>

<script>
    const API_BASE = 'https://group-matching-backend-production-4252.up.railway.app'; // 后端地址，不加端口
    
    // 全局状态
    let selectedSkills = new Set();
    let selectedThemes = new Set();
    let selectedTopics = new Set();
    
    // Topic 映射
    const topicMap = {
        'theme-a': [
            'Topic 1: Building the Next Big App',
            'Topic 2: AI Youth-Employment Brain',
            'Topic 3: AI for Sustainable Built Environment',
            'Topic 4: AI in Gaming',
            'Topic 5: Web Design',
            'Topic 6: AI in Accounting'
        ],
        'theme-b': [
            'Topic 1: Health-supporting Tech',
            'Topic 2: Smart Micro-Environment',
            'Topic 3: Smart Waste Watch',
            'Topic 4: CHIPS sensors',
            'Topic 5: Robot Roommate',
            'Topic 6: Robotics Perception'
        ],
        'theme-c': [
            'Topic 1: AI and 3D Printing',
            'Topic 2: Intelligent Transport',
            'Topic 3: Urban Regeneration',
            'Topic 4: Smart City',
            'Topic 5: AI in Home Design',
            'Topic 6: AI as Creative Partner'
        ],
        'theme-d': [
            'Topic 1: Nanomaterials',
            'Topic 2: Environmental Management',
            'Topic 3: AI in Healthcare',
            'Topic 4: Food Security',
            'Topic 5: Chemistry Research',
            'Topic 6: Climate Change'
        ],
        'theme-e': [
            'Topic 1: Urban ESG',
            'Topic 2: AI in Supply Chains',
            'Topic 3: Entrepreneurship',
            'Topic 4: Gold Trader',
            'Topic 5: AI Business Assistant',
            'Topic 6: Consumer Behavior'
        ],
        'theme-f': [
            'Topic 1: Image-Making',
            'Topic 2: Game Design',
            'Topic 3: Speculative Design',
            'Topic 4: AI in Social Media',
            'Topic 5: EcoArt',
            'Topic 6: Intercultural Communication'
        ],
        'theme-g': [
            'Topic 1: Ethical Dilemmas',
            'Topic 2: Professional Ethics',
            'Topic 3: Social Justice',
            'Topic 4: Intercultural Communication',
            'Topic 5: Globalization',
            'Topic 6: Future of Education'
        ],
        'theme-h': [
            'Topic 1: Academic Preparedness',
            'Topic 2: Career Planning',
            'Topic 3: Financial Literacy',
            'Topic 4: Life Skills',
            'Topic 5: Stress Management',
            'Topic 6: AI in Learning'
        ]
    };
    
    // 渲染 Topic 选项（基于已选 Theme）
    function renderTopics() {
        const container = document.getElementById('topicsContainer');
        if (!container) return;
        
        if (selectedThemes.size === 0) {
            container.innerHTML = '<div style="font-size: 0.8rem; color: #64748b;">💡 请先选择 Theme</div>';
            return;
        }
        
        // 收集所有已选 Theme 下的 Topic
        let allTopics = [];
        for (let theme of selectedThemes) {
            if (topicMap[theme]) {
                allTopics = allTopics.concat(topicMap[theme]);
            }
        }
        // 去重
        allTopics = [...new Set(allTopics)];
        
        let html = '<div style="margin-top: 8px;"><label>心仪 Topic（可多选）</label><div class="tags-group" id="topicTagsContainer">';
        allTopics.forEach(topic => {
            const isSelected = selectedTopics.has(topic);
            html += `<span class="topic-tag ${isSelected ? 'selected' : ''}" data-topic="${topic.replace(/"/g, '&quot;')}">📌 ${topic}</span>`;
        });
        html += '</div></div>';
        container.innerHTML = html;
        
        // 绑定 Topic 点击事件
        document.querySelectorAll('.topic-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const topic = tag.getAttribute('data-topic');
                if (selectedTopics.has(topic)) {
                    selectedTopics.delete(topic);
                    tag.classList.remove('selected');
                } else {
                    selectedTopics.add(topic);
                    tag.classList.add('selected');
                }
            });
        });
    }
    
    // 技能标签
    function initSkills() {
        document.querySelectorAll('.skill-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const skill = tag.getAttribute('data-skill');
                if (selectedSkills.has(skill)) {
                    selectedSkills.delete(skill);
                    tag.classList.remove('selected');
                } else {
                    selectedSkills.add(skill);
                    tag.classList.add('selected');
                }
            });
        });
    }
    
    // Theme 标签
    function initThemes() {
        document.querySelectorAll('.theme-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const theme = tag.getAttribute('data-theme');
                if (selectedThemes.has(theme)) {
                    selectedThemes.delete(theme);
                    tag.classList.remove('selected');
                } else {
                    selectedThemes.add(theme);
                    tag.classList.add('selected');
                }
                renderTopics();
            });
        });
    }
    
    // 聊天功能
    document.getElementById('chat-send-btn')?.addEventListener('click', () => {
        const input = document.getElementById('chat-input');
        const text = input?.value.trim();
        if (!text) { alert('请输入内容'); return; }
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message';
        msgDiv.innerHTML = `<strong>你：</strong>${text}`;
        document.getElementById('chatMessages').appendChild(msgDiv);
        input.value = '';
        localStorage.setItem('chatDiscussion', text);
        alert('已保存');
    });
    
    // 加载保存的聊天记录
    const savedChat = localStorage.getItem('chatDiscussion');
    if (savedChat && document.getElementById('chatMessages')) {
        const msg = document.createElement('div');
        msg.className = 'chat-message';
        msg.innerHTML = `<strong>📝 上次记录：</strong>${savedChat}`;
        document.getElementById('chatMessages').appendChild(msg);
    }
    
    // 人数滑块
    const rangeSlider = document.getElementById('groupSizeRange');
    const rangeValue = document.getElementById('groupSizeValue');
    if (rangeSlider) {
        rangeSlider.addEventListener('input', () => {
            rangeValue.textContent = rangeSlider.value + '人';
        });
    }
    
    function showMessage(id, text, isError) {
        const el = document.getElementById(id);
        if (!el) return;
        el.innerHTML = `<div style="background:${isError?'#f56565':'#10b981'};color:white;padding:12px;border-radius:12px;margin-bottom:16px;">${text}</div>`;
        setTimeout(() => { if (el) el.innerHTML = ''; }, 3000);
    }
    
    async function submitProfile() {
        // 收集数据
        const studentId = document.getElementById('studentId').value.trim();
        const name = document.getElementById('name').value.trim();
        const mbti = document.getElementById('mbti').value.trim();
        const personality = document.querySelector('input[name="personality"]:checked')?.value || '中性';
        const teamPersonality = document.querySelector('input[name="teamPersonality"]:checked')?.value || '多样化';
        const collabStyles = Array.from(document.querySelectorAll('input[name="collabStyle"]:checked')).map(cb => cb.value);
        const mainSkillLevel = document.getElementById('mainSkillLevel').value;
        const secSkillLevel = document.getElementById('secSkillLevel').value;
        const deadlineAttitude = document.querySelector('input[name="deadlineAttitude"]:checked')?.value || '';
        const needDivision = document.querySelector('input[name="needDivision"]:checked")?.value || '';
        const timeSlots = Array.from(document.querySelectorAll('input[name="timeSlots"]:checked')).map(cb => cb.value);
        const skillPreference = document.querySelector('input[name="skillPreference"]:checked")?.value || '互补';
        const chatBeforeTeam = document.querySelector('input[name="chatBeforeTeam"]:checked")?.value || '是';
        const additionalNote = document.getElementById('additionalNote')?.value || '';
        
        // 验证
        if (!studentId || !name) {
            showMessage('profileMsg', '请填写学号和姓名', true);
            return;
        }
        if (selectedSkills.size === 0) {
            showMessage('profileMsg', '请至少选择一个技能', true);
            return;
        }
        if (selectedThemes.size === 0) {
            showMessage('profileMsg', '请至少选择一个 Theme', true);
            return;
        }
        if (selectedTopics.size === 0) {
            showMessage('profileMsg', '请至少选择一个 Topic', true);
            return;
        }
        
        // 构建数据
        const data = {
            id: parseInt(studentId) || Date.now(),
            studentId: studentId,
            name: name,
            skills: Array.from(selectedSkills),
            level: mainSkillLevel,
            mbti: mbti,
            personality: personality,
            teamPersonality: teamPersonality,
            collabStyles: collabStyles,
            mainSkillLevel: mainSkillLevel,
            secSkillLevel: secSkillLevel,
            deadlineAttitude: deadlineAttitude,
            needDivision: needDivision,
            timeSlots: timeSlots,
            skillPreference: skillPreference,
            chatBeforeTeam: chatBeforeTeam,
            additionalNote: additionalNote,
            theme: Array.from(selectedThemes).join(','),
            topic: Array.from(selectedTopics).join(','),
            created_at: new Date().toISOString()
        };
        
        try {
            const response = await fetch(`${API_BASE}/api/participants`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                showMessage('profileMsg', '✅ 提交成功！已加入匹配池', false);
                // 清空表单
                document.getElementById('studentId').value = '';
                document.getElementById('name').value = '';
                selectedSkills.clear();
                selectedThemes.clear();
                selectedTopics.clear();
                document.querySelectorAll('.skill-tag, .theme-tag, .topic-tag').forEach(t => t.classList.remove('selected'));
                renderTopics();
            } else {
                showMessage('profileMsg', '提交失败：' + (result.error || '未知错误'), true);
            }
        } catch(e) {
            console.error(e);
            showMessage('profileMsg', '网络错误，请稍后重试', true);
        }
    }
    
    async function matchGroups() {
        const resultDiv = document.getElementById('matchResult');
        const targetSize = parseInt(document.getElementById('groupSizeRange')?.value || 8);
        resultDiv.innerHTML = '<div style="text-align:center;padding:20px;">✨ 匹配中...</div>';
        
        try {
            // 获取所有成员
            const res = await fetch(`${API_BASE}/api/participants`);
            const participants = await res.json();
            
            if (participants.length === 0) {
                resultDiv.innerHTML = '<div style="color:#f56565;text-align:center;">⚠️ 暂无成员，请先填写资料</div>';
                return;
            }
            
            // 调用后端匹配接口
            const matchRes = await fetch(`${API_BASE}/api/match`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    participants: participants, 
                    groupCount: Math.ceil(participants.length / targetSize),
                    minSize: 6,
                    maxSize: 10
                })
            });
            const result = await matchRes.json();
            
            if (result.groups && result.groups.length > 0) {
                let html = `<h3 style="margin-bottom:16px;">🎉 匹配结果</h3>`;
                html += `<p style="margin-bottom:16px; color:#64748b;">📊 总人数：${result.total_participants} | 已匹配：${result.matched_count} | 未匹配：${result.unmatched_count}</p>`;
                
                const colors = ['#3b82f6', '#8b5cf6', '#ec489a', '#f59e0b', '#10b981', '#ef4444'];
                result.groups.forEach((g, i) => {
                    const membersList = g.members.map(m => `${m.name} (${m.skills?.slice(0,2).join(',') || '无'})`).join('、');
                    html += `<div style="background:${colors[i%colors.length]}10; border-radius:16px; padding:16px; margin-bottom:16px; border-left: 4px solid ${colors[i%colors.length]};">
                        <strong style="color:${colors[i%colors.length]}">📌 第${g.id}组</strong> (${g.size}人)
                        <div style="margin-top:8px;"><strong>Theme/Topic：</strong> ${g.theme} / ${g.topic}</div>
                        <div style="margin-top:8px;"><strong>成员：</strong> ${membersList}</div>
                        <div style="font-size:12px; color:#64748b; margin-top:8px;">📊 组内匹配分：${g.internal_score}</div>
                    </div>`;
                });
                
                if (result.unmatched && result.unmatched.length > 0) {
                    html += `<div style="background:#fef2e8; border-radius:16px; padding:16px; margin-top:16px; border-left: 4px solid #f59e0b;">
                        <strong style="color:#f59e0b;">⚠️ 待讨论区（无法自动匹配）</strong>`;
                    result.unmatched.forEach(u => {
                        html += `<div style="margin-top:8px; padding:8px; background:white; border-radius:12px;">
                            <strong>${u.name}</strong><br>
                            <span style="font-size:12px;">${u.reason || '人数不足无法成组'}</span>
                        </div>`;
                    });
                    html += `</div>`;
                    html += `<div style="margin-top:16px; text-align:center;">
                        <button id="gotoChatBtn" style="background: linear-gradient(135deg, #f59e0b, #ef4444);">💬 前往讨论区商议</button>
