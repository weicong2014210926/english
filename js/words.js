// 英语趣学 H5 · 种子词库（MVP 演示，36 词，L1-L3）
// 字段: term 单词, phonetic 音标, level 级别, def 中文释义,
//       emoji 联想图, hook 记忆口诀(趣味钩子，与正确拼写视觉分离), example 例句
const WORD_BANK = [
  // ---------------- L1 基础 ----------------
  { term:'apple',      phonetic:'/ˈæp.əl/',     level:'L1', def:'苹果',     emoji:'🍎', hook:'红红的、咬一口脆甜——🍎 就是苹果', example:'I eat an apple every day.' },
  { term:'cat',        phonetic:'/kæt/',        level:'L1', def:'猫',       emoji:'🐱', hook:'喵星人，会撒娇的小动物', example:'The cat is sleeping.' },
  { term:'dog',        phonetic:'/dɒɡ/',        level:'L1', def:'狗',       emoji:'🐶', hook:'人类最忠诚的朋友', example:'A dog is a good friend.' },
  { term:'book',       phonetic:'/bʊk/',        level:'L1', def:'书',       emoji:'📖', hook:'知识的载体，翻开就有故事', example:'I read a book at night.' },
  { term:'water',      phonetic:'/ˈwɔː.tər/',   level:'L1', def:'水',       emoji:'💧', hook:'生命之源，渴了喝它', example:'Please drink more water.' },
  { term:'sun',        phonetic:'/sʌn/',        level:'L1', def:'太阳',     emoji:'☀️', hook:'白天发光发热的那颗恒星', example:'The sun is bright.' },
  { term:'happy',      phonetic:'/ˈhæp.i/',     level:'L1', def:'开心的',   emoji:'😊', hook:'心里甜丝丝的开心', example:'She is happy today.' },
  { term:'red',        phonetic:'/red/',        level:'L1', def:'红色',     emoji:'🔴', hook:'交通灯里“停”的颜色', example:'I like the red apple.' },
  { term:'eat',        phonetic:'/iːt/',        level:'L1', def:'吃',       emoji:'🍴', hook:'把食物送进嘴里的动作', example:'Let us eat lunch.' },
  { term:'go',         phonetic:'/ɡəʊ/',        level:'L1', def:'去；走',   emoji:'🚶', hook:'迈开腿往前走', example:'We go to school.' },
  { term:'tree',       phonetic:'/triː/',       level:'L1', def:'树',       emoji:'🌳', hook:'大地上的绿色大伞', example:'A bird is in the tree.' },
  { term:'fish',       phonetic:'/fɪʃ/',        level:'L1', def:'鱼',       emoji:'🐟', hook:'在水里游、不用肺呼吸的动物', example:'The fish swims fast.' },

  // ---------------- L2 进阶 ----------------
  { term:'ambulance',  phonetic:'/ˈæm.bjə.ləns/', level:'L2', def:'救护车', emoji:'🚑', hook:'发音联想“俺不能死”→ 救护车救人命（正确拼写 a-m-b-u-l-a-n-c-e）', example:'Call an ambulance now!' },
  { term:'bicycle',    phonetic:'/ˈbaɪ.sɪ.kl/',  level:'L2', def:'自行车', emoji:'🚲', hook:'两个轮子(bi=双)的骑车工具', example:'He rides a bicycle to work.' },
  { term:'forest',     phonetic:'/ˈfɒr.ɪst/',    level:'L2', def:'森林',   emoji:'🌲', hook:'很多树连成片的大森林', example:'They walked into the forest.' },
  { term:'secret',     phonetic:'/ˈsiː.krət/',   level:'L2', def:'秘密',   emoji:'🤫', hook:'不能说的悄悄话', example:'It is a secret between us.' },
  { term:'fragile',    phonetic:'/ˈfrædʒ.aɪl/', level:'L2', def:'易碎的', emoji:'🥚', hook:'像鸡蛋一样一碰就碎 → 易碎的', example:'The box is fragile.' },
  { term:'brilliant',  phonetic:'/ˈbrɪl.jənt/',  level:'L2', def:'聪明的；耀眼的', emoji:'💡', hook:'像灯泡突然亮了 → 聪明的/耀眼的', example:'She is a brilliant student.' },
  { term:'enormous',   phonetic:'/ɪˈnɔː.məs/',  level:'L2', def:'巨大的', emoji:'🐘', hook:'比大象还大 → 巨大的', example:'An enormous whale appeared.' },
  { term:'patient',    phonetic:'/ˈpeɪ.ʃənt/',   level:'L2', def:'病人；有耐心的', emoji:'🧘', hook:'生病时等你的是病人；能等的是有耐心的', example:'Be patient, it takes time.' },
  { term:'environment',phonetic:'/ɪnˈvaɪ.rən.mənt/', level:'L2', def:'环境', emoji:'🌍', hook:'我们周围的“环”境', example:'We must protect the environment.' },
  { term:'consider',   phonetic:'/kənˈsɪd.ər/',  level:'L2', def:'考虑',   emoji:'🤔', hook:'把事放在心里反复想 → 考虑', example:'Please consider my idea.' },
  { term:'whisper',    phonetic:'/ˈwɪs.pər/',    level:'L2', def:'耳语；低声说', emoji:'🤫', hook:'凑近耳朵轻轻说 → 耳语', example:'She whispered to me.' },
  { term:'mountain',   phonetic:'/ˈmaʊn.tən/',   level:'L2', def:'山',     emoji:'⛰️', hook:'高耸入云的大山', example:'We climbed the mountain.' },

  // ---------------- L3 高阶 ----------------
  { term:'ambition',   phonetic:'/æmˈbɪʃ.ən/', level:'L3', def:'野心；抱负', emoji:'🚀', hook:'心里有火想往上冲 → 野心/抱负', example:'His ambition is to be a pilot.' },
  { term:'circumstance',phonetic:'/ˈsɜː.kəm.stɑːns/', level:'L3', def:'环境；情况', emoji:'🔄', hook:'站在圆环(circle)里做事 → 周围的情况', example:'Under the circumstance, we waited.' },
  { term:'dilemma',    phonetic:'/dɪˈlem.ə/',  level:'L3', def:'困境；两难', emoji:'😣', hook:'两难(di=双)的困境', example:'He faced a real dilemma.' },
  { term:'elaborate',  phonetic:'/ɪˈlæb.ər.ət/', level:'L3', def:'精心制作的；详尽的', emoji:'🎨', hook:'往外(e-)劳动(labor)打磨 → 精心制作的', example:'She made an elaborate plan.' },
  { term:'phenomenon', phonetic:'/fəˈnɒm.ɪ.nən/', level:'L3', def:'现象', emoji:'🌈', hook:'天上出现的奇景 → 现象', example:'The rainbow is a natural phenomenon.' },
  { term:'spontaneous',phonetic:'/spɒnˈteɪ.ni.əs/', level:'L3', def:'自发的', emoji:'✨', hook:'自己(spon)冒出来的 → 自发的', example:'A spontaneous trip sounds fun.' },
  { term:'reluctant',  phonetic:'/rɪˈlʌk.tənt/', level:'L3', def:'不情愿的', emoji:'🛑', hook:'不肯往前 → 不情愿的', example:'He was reluctant to leave.' },
  { term:'tedious',    phonetic:'/ˈtiː.di.əs/', level:'L3', def:'冗长乏味的', emoji:'⏳', hook:'时间长到让人烦 → 冗长乏味的', example:'The meeting was tedious.' },
  { term:'vulnerable', phonetic:'/ˈvʌl.nər.ə.bəl/', level:'L3', def:'脆弱的', emoji:'🛡️', hook:'盾牌挡不住 → 脆弱的', example:'Children are vulnerable.' },
  { term:'alleviate',  phonetic:'/əˈliː.vi.eɪt/', level:'L3', def:'缓解；减轻', emoji:'🪶', hook:'把重量(lev)减轻 → 缓解', example:'This medicine alleviates pain.' },
  { term:'magnificent',phonetic:'/mæɡˈnɪf.ɪ.sənt/', level:'L3', def:'宏伟的；壮丽的', emoji:'👑', hook:'配得上加冕的 → 宏伟的/壮丽的', example:'What a magnificent view!' },
  { term:'subsequent', phonetic:'/ˈsʌb.sɪ.kwənt/', level:'L3', def:'随后的', emoji:'➡️', hook:'跟在(sub-)后面的 → 随后的', example:'Subsequent events proved him right.' }
];
