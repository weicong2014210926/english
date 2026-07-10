/* 英语趣学 H5 · 前端核心逻辑（纯原生 JS SPA，可直接浏览器运行）
   对应 PRD v0.2 + 技术方案：移动优先、图像故事联想、闯关积分、SM-2 间隔重复、暗色主题
   数据持久化: localStorage（后端就绪后替换为 Laravel API）
*/
(function () {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const todayStr = () => new Date().toISOString().slice(0, 10);

  /* ---------------- 存储层 ---------------- */
  const KEY = { prog: 'eq_progress', stat: 'eq_stats', set: 'eq_settings', ach: 'eq_ach' };
  const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));

  const defaultStats = { points: 0, weeklyPoints: 0, streak: 0, bestStreak: 0, lastCheckIn: '', learnedCount: 0, quizCorrect: 0, quizWrong: 0, levelDone: {} };
  let stats = Object.assign({}, defaultStats, load(KEY.stat, {}));
  let prog = load(KEY.prog, {});           // { term: {easeFactor,interval,repetitions,dueDate,learned,correct,wrong} }
  let settings = Object.assign({ theme: 'system', placementDone: false, placedLevel: null }, load(KEY.set, {}));
  let ach = load(KEY.ach, {});

  /* ---------------- 成就定义 ---------------- */
  const ACHIEVEMENTS = [
    { id: 'first_word', ic: '🌱', nm: '破土', ds: '学第一个词' },
    { id: 'quiz10', ic: '🎯', nm: '神枪手', ds: '测验答对 10 题' },
    { id: 'points100', ic: '💎', nm: '百宝箱', ds: '积分破 100' },
    { id: 'streak3', ic: '🔥', nm: '小火苗', ds: '连续签到 3 天' },
    { id: 'streak7', ic: '⚡', nm: '铁粉丝', ds: '连续签到 7 天' },
    { id: 'l1', ic: '🥉', nm: '入门', ds: '学完 L1' },
    { id: 'l2', ic: '🥈', nm: '进阶', ds: '学完 L2' },
    { id: 'l3', ic: '🥇', nm: '高阶', ds: '学完 L3' },
    { id: 'review', ic: '🔄', nm: '温故', ds: '完成一次复习' },
    { id: 'collector', ic: '⭐', nm: '收藏家', ds: '收藏 10 个生词' },
  ];

  /* ---------------- 工具 ---------------- */
  function speak(text) {
    if (!('speechSynthesis' in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = 0.9; u.pitch = 1;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  }

  function applyTheme() {
    let t = settings.theme;
    if (t === 'system') t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', t);
  }

  let toastTimer;
  function toast(msg) {
    let t = $('#toast');
    if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 1800);
  }

  function addPoints(p) { stats.points += p; stats.weeklyPoints += p; }

  function checkAch() {
    const unlock = (id) => {
      if (!ach[id]) { ach[id] = true; save(KEY.ach, ach); const a = ACHIEVEMENTS.find(x => x.id === id); toast('🏆 解锁成就 · ' + (a ? a.nm : id)); }
    };
    if (stats.learnedCount > 0) unlock('first_word');
    if (stats.quizCorrect >= 10) unlock('quiz10');
    if (stats.points >= 100) unlock('points100');
    if (stats.streak >= 3) unlock('streak3');
    if (stats.streak >= 7) unlock('streak7');
    ['L1', 'L2', 'L3'].forEach(l => { if (stats.levelDone[l]) unlock(l.toLowerCase()); });
    const favCount = Object.values(prog).filter(p => p && p.fav).length;
    if (favCount >= 10) unlock('collector');
  }

  /* ---------------- 词库辅助 ---------------- */
  const byLevel = (lv) => WORD_BANK.filter(w => w.level === lv);
  const levelTotal = (lv) => byLevel(lv).length;
  const levelLearned = (lv) => byLevel(lv).filter(w => prog[w.term] && prog[w.term].learned).length;
  const dueWords = () => WORD_BANK.filter(w => prog[w.term] && prog[w.term].learned && SM2.isDue(prog[w.term]));

  function startSession(level, isReview) {
    let list;
    if (isReview) {
      list = dueWords();
    } else {
      const pool = byLevel(level).filter(w => !(prog[w.term] && prog[w.term].learned));
      list = (pool.length ? pool : byLevel(level)).slice(0, 8);
    }
    if (!list.length) { toast('暂时没有可学的词啦 🎉'); return; }
    App.study = { level, isReview, list, idx: 0, quiz: [] };
    go('learn');
  }

  // 生词本：用户收藏的词 + 错多于对的词
  function vocabWords() {
    return WORD_BANK.filter(w => {
      const p = prog[w.term];
      return p && (p.fav || (p.wrong > p.correct));
    });
  }
  function vocabCount() { return vocabWords().length; }

  // 用自定义词列表开一组（生词巩固）
  function startCustom(list, title) {
    if (!list.length) { toast('还没有生词哦 📭'); return; }
    App.study = { level: title || 'vocab', isReview: true, list: list.slice(0, 10), idx: 0, quiz: [] };
    go('learn');
  }

  /* ---------------- 分级测评（自适应定档 F3） ---------------- */
  const LEVELS = ['L1', 'L2', 'L3'];
  function startPlacement() {
    App.place = { idx: 0, total: 12, correct: 0, band: 1, used: new Set(), result: null };
    go('place');
  }
  function placePickWord() {
    const p = App.place;
    let pool = byLevel(LEVELS[p.band - 1]).filter(w => !p.used.has(w.term));
    if (!pool.length) pool = WORD_BANK.filter(w => !p.used.has(w.term));
    if (!pool.length) pool = WORD_BANK;
    const w = pool[Math.floor(Math.random() * pool.length)];
    p.used.add(w.term);
    return w;
  }
  function viewPlace() {
    const p = App.place;
    if (p.result) return viewPlaceResult();
    const w = placePickWord();
    p._w = w;
    const opts = buildQuizOptions(w);
    p._opts = opts;
    return `<div class="study-wrap">
      <span class="progress-pill">🎯 分级测评 · ${p.idx + 1} / ${p.total} · 难度 L${p.band}</span>
      <div class="quiz-q">${w.emoji} ${w.term}</div>
      <div class="quiz-sub">${w.phonetic} · 选出正确中文释义（难度随答题自适应升降）</div>
      <div class="options">
        ${opts.map((o, i) => `<button class="option" data-i="${i}">${o.t}</button>`).join('')}
      </div>
      <div class="feedback" id="fb"></div>
    </div>`;
  }
  function bindPlace() {
    const p = App.place;
    $$('.option').forEach(btn => btn.onclick = () => {
      const i = +btn.dataset.i, opt = p._opts[i];
      $$('.option').forEach(b => b.classList.add('dim'));
      btn.classList.remove('dim');
      if (opt.ok) { btn.classList.add('correct'); p.correct++; }
      else { btn.classList.add('wrong'); $$('.option').forEach(b => { if (p._opts[+b.dataset.i].ok) b.classList.remove('dim'), b.classList.add('correct'); }); }
      const fb = $('#fb');
      fb.textContent = opt.ok ? '✅ 答对了！难度调高 🔼' : '❌ 答错了，难度调低 🔽';
      fb.className = 'feedback ' + (opt.ok ? 'ok' : 'no');
      $$('.option').forEach(b => b.onclick = null);
      p.band = opt.ok ? Math.min(3, p.band + 1) : Math.max(1, p.band - 1);
      p.idx++;
      setTimeout(() => { if (p.idx >= p.total) finishPlacement(); else render(); }, 650);
    });
  }
  function finishPlacement() {
    const p = App.place;
    const acc = p.correct / p.total;
    let level;
    if (acc <= 0.25) level = 'L1';
    else if (acc >= 0.85 && p.band === 3) level = 'L3';
    else {
      let b = p.band;
      if (b === 3 && acc < 0.5) b = 2; // 终点虽在高带但正确率不足，降一档
      level = LEVELS[b - 1];
    }
    p.result = { level, correct: p.correct, total: p.total, band: p.band, acc };
    settings.placementDone = true; settings.placedLevel = level; save(KEY.set, settings);
    render();
  }
  function viewPlaceResult() {
    const r = App.place.result;
    const lvName = { L1: 'L1 基础', L2: 'L2 进阶', L3: 'L3 高阶' }[r.level];
    const emoji = r.level === 'L3' ? '🚀' : r.level === 'L2' ? '🌿' : '🌱';
    return `<div class="study-wrap"><div class="result-card word-card">
      <div class="result-emoji">${emoji}</div>
      <div class="result-title">测评完成！</div>
      <div class="result-sub">推荐你从 <b>${lvName}</b> 开始</div>
      <div class="result-stats">
        <div><span>${r.correct}/${r.total}</span><small>答对</small></div>
        <div><span>${Math.round(r.acc * 100)}%</span><small>正确率</small></div>
        <div><span>L${r.band}</span><small>终点难度</small></div>
      </div>
      <div class="btn-row"><button class="btn" data-act="start-placed">▶ 从 ${lvName} 开始</button></div>
      <div class="btn-row">
        <button class="btn ghost" data-act="re-test">🔁 重新测评</button>
        <button class="btn ghost" data-act="home">🏠 返回首页</button>
      </div>
    </div></div>`;
  }
  function bindPlaceResult() {
    $('[data-act="start-placed"]').onclick = () => startSession(settings.placedLevel, false);
    $('[data-act="re-test"]').onclick = () => startPlacement();
    $('[data-act="home"]').onclick = () => go('home');
  }

  /* ---------------- 渲染框架 ---------------- */
  const App = { view: 'home', study: null };
  const app = () => $('#app');

  function tabBar() {
    const items = [
      { id: 'home', ti: '🏠', tx: '首页' },
      { id: 'vocab', ti: '📕', tx: '生词' },
      { id: 'review', ti: '🔄', tx: '复习' },
      { id: 'lb', ti: '🏆', tx: '排行' },
      { id: 'ach', ti: '⭐', tx: '成就' },
    ];
    return `<nav class="tabbar">${items.map(i => `<div class="tab ${App.view === i.id ? 'active' : ''}" data-nav="${i.id}"><span class="ti">${i.ti}</span><span>${i.tx}</span></div>`).join('')}</nav>`;
  }

  function topbar(title) {
    return `<header class="topbar">
      <div class="brand"><span class="logo">🦊</span><div>趣学英语<small>ENJOY · LEARN</small></div></div>
      <div class="top-actions"><button class="icon-btn" data-act="theme" title="主题">${settings.theme === 'dark' ? '🌙' : settings.theme === 'light' ? '☀️' : '🌀'}</button></div>
    </header>`;
  }

  function render() {
    let html = '';
    if (App.view === 'home') html = viewHome();
    else if (App.view === 'learn') html = viewLearn();
    else if (App.view === 'quiz') html = viewQuiz();
    else if (App.view === 'result') html = viewResult();
    else if (App.view === 'review') html = viewReviewList();
    else if (App.view === 'lb') html = viewLeaderboard();
    else if (App.view === 'ach') html = viewAchievements();
    else if (App.view === 'vocab') html = viewVocab();
    else if (App.view === 'place') html = (App.place && App.place.result) ? viewPlaceResult() : viewPlace();

    app().innerHTML = topbar() + `<div class="view">${html}</div>` + tabBar();
    bindCommon();
    if (App.view === 'home') bindHome();
    else if (App.view === 'learn') bindLearn();
    else if (App.view === 'quiz') bindQuiz();
    else if (App.view === 'result') bindResult();
    else if (App.view === 'review') bindReviewList();
    else if (App.view === 'vocab') bindVocab();
    else if (App.view === 'place') { if (App.place && App.place.result) bindPlaceResult(); else bindPlace(); }
  }

  function go(v) { App.view = v; render(); window.scrollTo(0, 0); }

  function bindCommon() {
    $$('[data-nav]').forEach(b => b.onclick = () => go(b.dataset.nav));
    $$('[data-act="theme"]').forEach(b => b.onclick = openThemeSheet);
  }

  /* ---------------- 首页 ---------------- */
  function viewHome() {
    const canCheckIn = stats.lastCheckIn !== todayStr();
    const due = dueWords().length;
    const checkin = canCheckIn
      ? `<div class="checkin" data-act="checkin"><div class="ci-emoji">📅</div><div class="ci-meta"><h4>每日签到 +10 积分</h4><p>已连续 ${stats.streak} 天，点我领今日奖励</p></div><div class="btn soft">签到</div></div>`
      : `<div class="checkin"><div class="ci-emoji">✅</div><div class="ci-meta"><h4>今日已签到</h4><p>连续 ${stats.streak} 天 · 明天再来</p></div></div>`;

    const levelCard = (lv, emoji, name, desc) => {
      const total = levelTotal(lv), learned = levelLearned(lv), pct = total ? Math.round(learned / total * 100) : 0;
      const done = learned >= total && total > 0;
      const rec = (settings.placementDone && settings.placedLevel === lv) ? ' · ⭐推荐' : '';
      return `<div class="level-card" data-level="${lv}">
        <div class="emoji">${emoji}</div>
        <div class="meta"><h3>${name} ${done ? '🎉' : ''}</h3><p>${desc}${rec} · 已学 ${learned}/${total}</p>
          <div class="progress"><i style="width:${pct}%"></i></div></div>
        <div class="go">›</div></div>`;
    };

    const placementCard = !settings.placementDone
      ? `<div class="level-card" data-act="place" style="border-color:var(--glass-border-strong);background:linear-gradient(135deg, rgba(124,58,237,.14), rgba(245,158,11,.12))"><div class="emoji">🎯</div><div class="meta"><h3>分级测评（推荐先做）</h3><p>12 题自适应测试，为你智能定档 L1–L3</p></div><div class="go">›</div></div>`
      : `<div class="level-card" data-act="place" style="border-color:var(--glass-border-strong)"><div class="emoji">🎯</div><div class="meta"><h3>重新分级测评</h3><p>上次推荐：从 ${settings.placedLevel} 开始 · 想换档可重测</p></div><div class="go">›</div></div>`;

    return `
      ${checkin}
      <div class="stats-row">
        <div class="stat-card"><div class="num">${stats.points}</div><div class="lbl">总积分</div></div>
        <div class="stat-card"><div class="num">${stats.streak}</div><div class="lbl">连续签到</div></div>
        <div class="stat-card"><div class="num">${stats.learnedCount}</div><div class="lbl">已学词</div></div>
      </div>
      ${placementCard}
      <div class="section-title"><span class="bar"></span>开始学习</div>
      ${levelCard('L1', '🌱', 'L1 基础', '生活高频词')}
      ${levelCard('L2', '🌿', 'L2 进阶', '场景进阶词')}
      ${levelCard('L3', '🌳', 'L3 高阶', '考试核心词')}
      ${vocabCount() > 0 ? `<div class="level-card" data-vocab="1" style="border-color:var(--glass-border-strong)"><div class="emoji">📕</div><div class="meta"><h3>我的生词本</h3><p>已收藏 / 易错 ${vocabCount()} 个词，常回来看看</p></div><div class="go">›</div></div>` : ''}
      ${due > 0 ? `<div class="level-card" data-review="1" style="border-color:var(--glass-border-strong)"><div class="emoji">🔄</div><div class="meta"><h3>复习待巩固词</h3><p>有 ${due} 个词到期，温故知新</p></div><div class="go">›</div></div>` : ''}
    `;
  }

  function bindHome() {
    $$('[data-level]').forEach(c => c.onclick = () => startSession(c.dataset.level, false));
    const rv = $('[data-review]'); if (rv) rv.onclick = () => startSession(null, true);
    const vb = $('[data-vocab]'); if (vb) vb.onclick = () => go('vocab');
    const pc = $('[data-act="place"]'); if (pc) pc.onclick = startPlacement;
    const ci = $('[data-act="checkin"]');
    if (ci) ci.onclick = () => {
      if (stats.lastCheckIn === todayStr()) return;
      const yest = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
      stats.streak = (stats.lastCheckIn === yest) ? stats.streak + 1 : 1;
      stats.bestStreak = Math.max(stats.bestStreak, stats.streak);
      stats.lastCheckIn = todayStr();
      addPoints(10); checkAch(); save(KEY.stat, stats);
      toast(`签到成功 · 连续 ${stats.streak} 天 +10 🔥`);
      render();
    };
  }

  /* ---------------- 学习（联想）阶段 ---------------- */
  function viewLearn() {
    const s = App.study, w = s.list[s.idx];
    const step = `${s.idx + 1} / ${s.list.length}`;
    return `<div class="study-wrap">
      <span class="progress-pill">📚 ${s.isReview ? '复习' : '学习'} · ${step}</span>
      <div class="word-card hidden-state" id="wcard">
        <div class="word-emoji">${w.emoji}</div>
        <div class="word-term">${w.term}</div>
        <div class="word-phon">${w.phonetic}</div>
        <button class="speak-btn" data-act="speak">🔊 听发音</button>
        <div class="reveal">
          <div class="def">${w.def}<span class="pos">${w.level}</span></div>
          <div class="hook"><span class="tag">💡 联想记忆</span><br>${w.hook}</div>
          <div class="example">“<b>${w.example}</b>”</div>
        </div>
      </div>
      <div class="btn-row">
        <button class="btn ghost" data-act="reveal">👀 看释义 / 联想</button>
      </div>
      <div class="btn-row" id="assess" style="display:none">
        <button class="btn ghost" data-q="2">😵 没记住</button>
        <button class="btn ghost" data-q="3">🤔 模糊</button>
        <button class="btn success" data-q="5">😎 记住了</button>
      </div>
      <div class="btn-row" id="favRow" style="display:none;justify-content:center">
        <button class="btn ghost" data-act="fav">⭐ 收藏生词</button>
      </div>
    </div>`;
  }

  function bindLearn() {
    const card = $('#wcard');
    const term = App.study.list[App.study.idx].term;
    $('[data-act="speak"]').onclick = () => speak(term);
    $('[data-act="reveal"]').onclick = () => {
      card.classList.remove('hidden-state'); card.classList.add('reveal-state');
      $('[data-act="reveal"]').style.display = 'none';
      $('#assess').style.display = 'flex';
      const fr = $('#favRow');
      if (fr) {
        fr.style.display = 'flex';
        const fb = $('[data-act="fav"]');
        if (fb) fb.textContent = (prog[term] && prog[term].fav) ? '⭐ 已收藏' : '⭐ 收藏生词';
      }
    };
    const favBtn = $('[data-act="fav"]');
    if (favBtn) favBtn.onclick = () => {
      const p = prog[term] || (prog[term] = { learned: false, correct: 0, wrong: 0, easeFactor: 2.5, interval: 0, repetitions: 0, dueDate: todayStr(), fav: false });
      p.fav = !p.fav; save(KEY.prog, prog);
      favBtn.textContent = p.fav ? '⭐ 已收藏' : '⭐ 收藏生词';
      toast(p.fav ? '已加入生词本 ⭐' : '已取消收藏');
    };
    $$('#assess [data-q]').forEach(b => b.onclick = () => {
      const q = +b.dataset.q;
      App.study.quiz.push({ term: term, quality: q });
      nextLearn();
    });
  }

  function nextLearn() {
    App.study.idx++;
    if (App.study.idx >= App.study.list.length) {
      // 学完进入测验
      App.study.quizIdx = 0; App.study.quizCorrect = 0;
      go('quiz');
    } else render();
  }

  /* ---------------- 测验阶段 ---------------- */
  function buildQuizOptions(word) {
    const correct = word.def;
    const pool = WORD_BANK.filter(w => w.def !== correct).map(w => w.def);
    const distract = [];
    while (distract.length < 3 && pool.length) distract.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
    const opts = [{ t: correct, ok: true }].concat(distract.map(d => ({ t: d, ok: false })));
    for (let i = opts.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[opts[i], opts[j]] = [opts[j], opts[i]]; }
    return opts;
  }

  function viewQuiz() {
    const s = App.study, w = s.list[s.quizIdx];
    const opts = buildQuizOptions(w);
    s._opts = opts;
    const mode = Math.random() < 0.5 ? 'listen' : 'choice';
    s._mode = mode;
    const qHtml = mode === 'listen'
      ? `<div class="quiz-q listen">
           <button class="speak-big" data-act="speak">🔊</button>
           <div class="quiz-sub">点击听发音，选出正确中文释义</div>
           <div class="hidden-term" id="hiddenTerm" style="display:none">${w.term} <small>${w.phonetic}</small></div>
         </div>`
      : `<div class="quiz-q">${w.emoji} ${w.term}</div>
         <div class="quiz-sub">${w.phonetic} · 选出正确中文释义</div>`;
    return `<div class="study-wrap">
      <span class="progress-pill">🧠 测验 · ${s.quizIdx + 1} / ${s.list.length}${mode === 'listen' ? ' · 🔊 听音' : ''}</span>
      ${qHtml}
      <div class="options">
        ${opts.map((o, i) => `<button class="option" data-i="${i}">${o.t}</button>`).join('')}
      </div>
      <div class="feedback" id="fb"></div>
      <button class="btn block" id="nextBtn" style="margin-top:14px;display:none" data-act="next">下一题 ›</button>
    </div>`;
  }

  function bindQuiz() {
    const s = App.study;
    // 听音模式：自动播放发音 + 绑定重播按钮
    if (s._mode === 'listen') {
      const sb = $('[data-act="speak"]');
      if (sb) sb.onclick = () => speak(s.list[s.quizIdx].term);
      speak(s.list[s.quizIdx].term);
    }
    $$('.option').forEach(btn => btn.onclick = () => {
      const i = +btn.dataset.i, opt = s._opts[i];
      $$('.option').forEach(b => b.classList.add('dim'));
      btn.classList.remove('dim');
      if (opt.ok) { btn.classList.add('correct'); s.quizCorrect++; }
      else { btn.classList.add('wrong'); $$('.option').forEach(b => { if (s._opts[+b.dataset.i].ok) b.classList.remove('dim'), b.classList.add('correct'); }); }
      const fb = $('#fb');
      fb.textContent = opt.ok ? '✅ 答对啦！' : '❌ 正确答案：' + s._opts.find(o => o.ok).t;
      fb.className = 'feedback ' + (opt.ok ? 'ok' : 'no');
      // 听音模式下答完揭示单词与音标
      if (s._mode === 'listen') { const ht = $('#hiddenTerm'); if (ht) ht.style.display = 'block'; }
      $$('.option').forEach(b => b.onclick = null);
      $('#nextBtn').style.display = 'block';
      // 记录测验正确/错误用于 SM-2
      const rec = s.quiz.find(q => q.term === s.list[s.quizIdx].term);
      if (rec) rec.quizCorrect = opt.ok;
    });
    $('#nextBtn').onclick = () => {
      s.quizIdx++;
      if (s.quizIdx >= s.list.length) finishSession(); else render();
    };
  }

  function finishSession() {
    const s = App.study;
    // 合并学习自评 quality 与测验结果，推进 SM-2
    s.quiz.forEach(q => {
      const w = WORD_BANK.find(x => x.term === q.term);
      const learnQ = q.quality || 3;
      const finalQ = q.quizCorrect ? Math.max(learnQ, 4) : 2; // 测验错则强制低质量
      const prev = prog[q.term] || Object.assign({ learned: false, correct: 0, wrong: 0 }, SM2.fresh());
      const next = SM2.review(prev, finalQ);
      const wasLearned = prev.learned;
      prog[q.term] = Object.assign({}, prev, next, { learned: true });
      if (!wasLearned) stats.learnedCount++;
      if (q.quizCorrect) { stats.quizCorrect++; prog[q.term].correct++; addPoints(12); }
      else { stats.quizWrong++; prog[q.term].wrong++; addPoints(3); }
    });
    // 关卡完成判定
    if (!s.isReview) {
      const lv = s.level;
      if (levelLearned(lv) >= levelTotal(lv) && levelTotal(lv) > 0) stats.levelDone[lv] = true;
    }
    if (s.isReview) { const a = ach; if (!a.review) { ach.review = true; } }
    checkAch();
    save(KEY.prog, prog); save(KEY.stat, stats); save(KEY.ach, ach);
    App.result = { correct: s.quizCorrect, total: s.list.length, points: s.quiz.reduce((s2, q) => s2 + (q.quizCorrect ? 12 : 3), 0), isReview: s.isReview, level: s.level };
    go('result');
  }

  /* ---------------- 结果 ---------------- */
  function viewResult() {
    const r = App.result;
    const rate = Math.round(r.correct / r.total * 100);
    const emoji = rate >= 90 ? '🏆' : rate >= 60 ? '🎉' : '💪';
    const title = rate >= 90 ? '完美通关！' : rate >= 60 ? '不错哦～' : '继续加油！';
    return `<div class="study-wrap"><div class="result-card word-card">
      <div class="result-emoji">${emoji}</div>
      <div class="result-title">${title}</div>
      <div class="result-sub">${r.isReview ? '复习' : (r.level + ' 学习')}完成</div>
      <div class="result-stats">
        <div><span>${r.correct}/${r.total}</span><small>正确</small></div>
        <div><span>+${r.points}</span><small>获得积分</small></div>
        <div><span>${rate}%</span><small>正确率</small></div>
      </div>
      <div class="btn-row">
        <button class="btn ghost" data-act="home">🏠 首页</button>
        <button class="btn" data-act="again">🔁 再来一组</button>
      </div>
    </div></div>`;
  }

  function bindResult() {
    $('[data-act="home"]').onclick = () => go('home');
    $('[data-act="again"]').onclick = () => { const s = App.study; startSession(s.level, s.isReview); };
  }

  /* ---------------- 复习列表 ---------------- */
  function viewReviewList() {
    const due = dueWords();
    if (!due.length) return `<div class="empty"><span class="e-emoji">🌟</span>暂无到期复习的词<br>学完一组后，隔天再回来巩固吧</div>`;
    return `<div class="section-title"><span class="bar"></span>待复习 ${due.length} 词</div>
      <div class="level-card" data-review="1"><div class="emoji">🔄</div><div class="meta"><h3>开始复习</h3><p>温故知新，巩固记忆曲线</p></div><div class="go">›</div></div>`;
  }
  function bindReviewList() { const rv = $('[data-review]'); if (rv) rv.onclick = () => startSession(null, true); }

  /* ---------------- 生词本 ---------------- */
  function viewVocab() {
    const list = vocabWords();
    if (!list.length) return `<div class="empty"><span class="e-emoji">📭</span>生词本是空的<br>学习时点 ⭐ 收藏，或答错的词会自动进来</div>`;
    return `<div class="section-title"><span class="bar"></span>我的生词本（${list.length}）</div>
      <p style="color:var(--text-soft);font-size:12px;margin:0 4px 12px">点单词可听发音，点「开始巩固」集中复习 💪</p>
      <div class="vocab-list">
        ${list.map(w => `<div class="vocab-item" data-term="${w.term}">
          <span class="v-emoji">${w.emoji}</span>
          <span class="v-term">${w.term}</span>
          <span class="v-def">${w.def}</span>
          ${prog[w.term] && prog[w.term].fav ? '<span class="v-fav">⭐</span>' : ''}
          <button class="v-spk" data-spk="${w.term}">🔊</button>
        </div>`).join('')}
      </div>
      <button class="btn block" data-act="vocab-review" style="margin-top:14px">🔁 开始巩固这 ${list.length} 个词</button>`;
  }
  function bindVocab() {
    $$('[data-spk]').forEach(b => b.onclick = (e) => { e.stopPropagation(); speak(b.dataset.spk); });
    const rv = $('[data-act="vocab-review"]'); if (rv) rv.onclick = () => startCustom(vocabWords(), '生词巩固');
  }

  /* ---------------- 排行榜（本地模拟，后端接实时快照） ---------------- */
  function viewLeaderboard() {
    const bots = [
      { n: 'Lexie', a: '🦄', p: 320 }, { n: '阿杰', a: '🐯', p: 268 }, { n: 'Momo', a: '🐱', p: 240 },
      { n: '小王', a: '🐼', p: 198 }, { n: 'Coco', a: '🐰', p: 165 }, { n: '大壮', a: '🐻', p: 132 },
    ];
    const me = { n: '我', a: '🦊', p: stats.weeklyPoints, me: true };
    const list = bots.concat([me]).sort((a, b) => b.p - a.p);
    return `<div class="section-title"><span class="bar"></span>本周排行榜</div>
      <p style="color:var(--text-soft);font-size:12px;margin:0 4px 12px">积分越高排名越靠前，每天学习 + 签到冲刺榜首 🏆</p>
      ${list.map((u, i) => `<div class="lb-row ${u.me ? 'me' : ''}">
        <div class="lb-rank ${i < 3 ? 'top' : ''}">${i === 0 ? '👑' : i + 1}</div>
        <div class="lb-ava">${u.a}</div>
        <div class="lb-name">${u.n}${u.me ? '<small>这就是你</small>' : ''}</div>
        <div class="lb-pts">${u.p}</div>
      </div>`).join('')}`;
  }

  /* ---------------- 成就 ---------------- */
  function viewAchievements() {
    return `<div class="section-title"><span class="bar"></span>我的成就（${Object.keys(ach).length}/${ACHIEVEMENTS.length}）</div>
      <div class="ach-grid">
        ${ACHIEVEMENTS.map(a => `<div class="ach ${ach[a.id] ? '' : 'locked'}"><div class="ic">${a.ic}</div><div class="nm">${a.nm}</div><div class="ds">${a.ds}</div></div>`).join('')}
      </div>`;
  }

  /* ---------------- 主题弹层 ---------------- */
  function openThemeSheet() {
    const mask = document.createElement('div'); mask.className = 'sheet-mask';
    mask.innerHTML = `<div class="sheet"><h4>🎨 选择主题</h4>
      ${[['light', '☀️', '亮色', '始终浅色界面'], ['dark', '🌙', '暗色', '护眼深色界面'], ['system', '🌀', '跟随系统', '随设备自动切换']].map(([v, ic, tx, ds]) => `<div class="theme-opt ${settings.theme === v ? 'active' : ''}" data-theme="${v}"><div class="sw ${v === 'light' ? 'l' : v === 'dark' ? 'd' : 's'}"></div><div class="tx">${ic} ${tx}<small>${ds}</small></div><div>${settings.theme === v ? '✓' : ''}</div></div>`).join('')}
      <button class="btn block ghost" data-close style="margin-top:6px">关闭</button></div>`;
    document.body.appendChild(mask);
    mask.onclick = (e) => { if (e.target === mask || e.target.dataset.close !== undefined) mask.remove(); };
    $$('.theme-opt', mask).forEach(o => o.onclick = () => {
      settings.theme = o.dataset.theme; save(KEY.set, settings); applyTheme(); mask.remove(); toast('主题已切换'); render();
    });
  }

  /* ---------------- 启动 ---------------- */
  applyTheme();
  // 首次进入引导
  if (!localStorage.getItem('eq_seen')) { save('eq_seen', 1); }
  render();
  window.addEventListener('storage', () => { prog = load(KEY.prog, {}); stats = Object.assign({}, defaultStats, load(KEY.stat, {})); render(); });
})();
