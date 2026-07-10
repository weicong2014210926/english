# -*- coding: utf-8 -*-
"""
英语趣学 H5 · 词库生成器 (MVP 演示)
- 单一数据源：本脚本产出 js/words.js（前端原型用）
- 结构对齐将来 Laravel WordSeeder：term/phonetic/level/def/emoji/hook/example
- 后续可改成读取 GSL + CET-4 + CC-CEDICT 生成，字段不变即可直接复用
用法: python tools/gen_words.py  -> 写入 js/words.js
"""
import json, os, sys

# emoji 兜底映射（具体名词自动配图，抽象词给通用图标）
EMOJI_MAP = {
    'apple':'🍎','cat':'🐱','dog':'🐶','book':'📖','water':'💧','sun':'☀️','happy':'😊',
    'red':'🔴','eat':'🍴','go':'🚶','tree':'🌳','fish':'🐟','ambulance':'🚑','bicycle':'🚲',
    'forest':'🌲','secret':'🤫','fragile':'🥚','brilliant':'💡','enormous':'🐘','patient':'🧘',
    'environment':'🌍','consider':'🤔','whisper':'🤫','mountain':'⛰️','ambition':'🚀','circumstance':'🔄',
    'dilemma':'😣','elaborate':'🎨','phenomenon':'🌈','spontaneous':'✨','reluctant':'🛑','tedious':'⏳',
    'vulnerable':'🛡️','alleviate':'🪶','magnificent':'👑','subsequent':'➡️','bird':'🐦','egg':'🥚',
    'milk':'🥛','school':'🏫','teacher':'👩‍🏫','student':'🧑‍🎓','friend':'🤝','family':'👨‍👩‍👧',
    'house':'🏠','car':'🚗','bus':'🚌','train':'🚄','flower':'🌸','grass':'🌿','rain':'🌧️',
    'snow':'❄️','fire':'🔥','star':'⭐','moon':'🌙','night':'🌃','morning':'🌅','food':'🍲',
    'fruit':'🍓','vegetable':'🥦','rice':'🍚','bread':'🍞','meat':'🥩','door':'🚪','window':'🪟',
    'chair':'🪑','table':'🛋️','pen':'🖊️','paper':'📄','phone':'📱','computer':'💻','money':'💰',
    'time':'⏰','day':'📅','week':'🗓️','month':'📆','year':'🎉','weather':'🌤️','wind':'🌬️',
    'cloud':'☁️','light':'💡','dark':'🌑','cold':'🥶','hot':'🥵','warm':'🌡️','clean':'🧼',
    'dirty':'🪣','new':'🆕','old':'👴','big':'🐘','small':'🔹','fast':'💨','slow':'🐢',
    'high':'📏','low':'🔻','open':'🔓','close':'🔒','read':'📖','write':'✍️','listen':'👂',
    'speak':'🗣️','walk':'🚶','run':'🏃','jump':'🦘','swim':'🏊','sleep':'😴','wake':'⏰',
    'work':'💼','play':'🎮','sing':'🎤','dance':'💃','smile':'😄','cry':'😢','love':'❤️',
    'hate':'💢','help':'🆘','learn':'📚','think':'💭','know':'🧠','forget':'🤷','remember':'💾',
    'believe':'🙏','hope':'🌟','dream':'💭','wish':'⭐','peace':'🕊️','war':'⚔️','life':'🌱',
    'death':'💀','city':'🏙️','town':'🏘️','road':'🛣️','bridge':'🌉','river':'🌊','lake':'🏞️',
    'sea':'🌊','beach':'🏖️','island':'🏝️','field':'🌾','farm':'🚜','animal':'🐾','plant':'🌱',
    'spring':'🌸','summer':'☀️','autumn':'🍂','winter':'❄️','air':'💨','earth':'🌍','space':'🚀',
    'science':'🔬','art':'🎨','music':'🎵','sport':'⚽','game':'🎲','movie':'🎬','story':'📖',
    'song':'🎶','color':'🎨','number':'🔢','letter':'✉️','word':'🔤','name':'🏷️','question':'❓',
    'answer':'✅','problem':'⚠️','idea':'💡','plan':'📋','goal':'🎯','success':'🏆','fail':'💥',
    'win':'🥇','lose':'😞','strong':'💪','weak':'🥀','healthy':'💪','sick':'🤒','doctor':'🩺',
    'medicine':'💊','hospital':'🏥','market':'🛒','shop':'🏪','store':'🏬','bank':'🏦','post':'📮',
    'letter_mail':'✉️','gift':'🎁','party':'🎉','festival':'🎊','holiday':'🏖️','travel':'✈️','trip':'🧳',
    'country':'🏳️','world':'🌐','language':'🗣️','culture':'🏛️','history':'📜','future':'🔮','past':'⏳',
    'present':'🎁','child':'🧒','baby':'👶','man':'👨','woman':'👩','people':'👥','crowd':'👥',
}

def emoji_of(term, fallback='📝'):
    return EMOJI_MAP.get(term, fallback)

# 词库（演示用，精选高频 + 趣味联想）
# 字段: term, phonetic, level, def, emoji(None=自动), hook, example
RAW = [
    # ---------------- L1 基础（生活高频） ----------------
    ('apple','/ˈæp.əl/','L1','苹果','🍎','红红的、咬一口脆甜——🍎 就是苹果','I eat an apple every day.'),
    ('cat','/kæt/','L1','猫','🐱','喵星人，会撒娇的小动物','The cat is sleeping.'),
    ('dog','/dɒɡ/','L1','狗','🐶','人类最忠诚的朋友','A dog is a good friend.'),
    ('book','/bʊk/','L1','书','📖','知识的载体，翻开就有故事','I read a book at night.'),
    ('water','/ˈwɔː.tər/','L1','水','💧','生命之源，渴了喝它','Please drink more water.'),
    ('sun','/sʌn/','L1','太阳','☀️','白天发光发热的那颗恒星','The sun is bright.'),
    ('happy','/ˈhæp.i/','L1','开心的','😊','心里甜丝丝的开心','She is happy today.'),
    ('red','/red/','L1','红色','🔴','交通灯里“停”的颜色','I like the red apple.'),
    ('eat','/iːt/','L1','吃','🍴','把食物送进嘴里的动作','Let us eat lunch.'),
    ('go','/ɡəʊ/','L1','去；走','🚶','迈开腿往前走','We go to school.'),
    ('tree','/triː/','L1','树','🌳','大地上的绿色大伞','A bird is in the tree.'),
    ('fish','/fɪʃ/','L1','鱼','🐟','在水里游、不用肺呼吸的动物','The fish swims fast.'),
    ('bird','/bɜːd/','L1','鸟','🐦','长翅膀会飞的小动物','A bird is singing.'),
    ('egg','/eɡ/','L1','蛋','🥚','小鸡破壳前住的地方','I had an egg for breakfast.'),
    ('milk','/mɪlk/','L1','牛奶','🥛','奶牛给的白白营养饮品','Drink milk before bed.'),
    ('school','/skuːl/','L1','学校','🏫','每天去学知识的地方','We go to school by bus.'),
    ('friend','/frend/','L1','朋友','🤝','一起玩、互相帮的人','He is my best friend.'),
    ('house','/haʊs/','L1','房子','🏠','一家人住的小窝','Our house is near the park.'),
    ('car','/kɑːr/','L1','汽车','🚗','四个轮子带你去远方','The red car is fast.'),
    ('flower','/ˈflaʊ.ər/','L1','花','🌸','香香的、蜜蜂爱采它','She picked a flower.'),
    ('rain','/reɪn/','L1','雨','🌧️','天上掉下来的水珠','The rain stopped at noon.'),
    ('star','/stɑːr/','L1','星星','⭐','夜里天上眨眼的亮点','I wish upon a star.'),
    ('sleep','/sliːp/','L1','睡觉','😴','闭眼充电的休息时间','The baby is asleep.'),
    ('run','/rʌn/','L1','跑','🏃','比走快得多的移动','He can run very fast.'),
    # ---- L1 扩充（身体/家庭/食物/颜色/常用词） ----
    ('eye','/aɪ/','L1','眼睛','👁️'),
    ('hand','/hænd/','L1','手','✋'),
    ('foot','/fʊt/','L1','脚','🦶'),
    ('head','/hed/','L1','头','🙆'),
    ('mouth','/maʊθ/','L1','嘴','👄'),
    ('nose','/nəʊz/','L1','鼻子','👃'),
    ('ear','/ɪər/','L1','耳朵','👂'),
    ('face','/feɪs/','L1','脸','😊'),
    ('hair','/heər/','L1','头发','💇'),
    ('mother','/ˈmʌð.ər/','L1','妈妈','👩'),
    ('father','/ˈfɑː.ðər/','L1','爸爸','👨'),
    ('brother','/ˈbrʌð.ər/','L1','兄弟','👦'),
    ('sister','/ˈsɪs.tər/','L1','姐妹','👧'),
    ('boy','/bɔɪ/','L1','男孩','👦'),
    ('girl','/ɡɜːl/','L1','女孩','👧'),
    ('teacher','/ˈtiː.tʃər/','L1','老师','👩‍🏫'),
    ('student','/ˈstjuː.dənt/','L1','学生','🧑‍🎓'),
    ('bag','/bæɡ/','L1','书包','🎒'),
    ('pen','/pen/','L1','钢笔','🖊️'),
    ('tea','/tiː/','L1','茶','🍵'),
    ('coffee','/ˈkɒf.i/','L1','咖啡','☕'),
    ('sugar','/ˈʃʊɡ.ər/','L1','糖','🍬'),
    ('salt','/sɔːlt/','L1','盐','🧂'),
    ('ball','/bɔːl/','L1','球','⚽'),
    ('toy','/tɔɪ/','L1','玩具','🧸'),
    ('blue','/bluː/','L1','蓝色','🔵'),
    ('green','/ɡriːn/','L1','绿色','🟢'),
    ('yellow','/ˈjel.əʊ/','L1','黄色','🟡'),
    ('black','/blæk/','L1','黑色','⚫'),
    ('white','/waɪt/','L1','白色','⚪'),
    ('good','/ɡʊd/','L1','好的','👍'),
    ('bad','/bæd/','L1','坏的','👎'),
    ('today','/təˈdeɪ/','L1','今天','📅'),
    ('tomorrow','/təˈmɒr.əʊ/','L1','明天','📆'),
    ('hello','/həˈləʊ/','L1','你好','👋'),
    ('thanks','/θæŋks/','L1','谢谢','🙏'),
    ('please','/pliːz/','L1','请','🤲'),
    ('sorry','/ˈsɒr.i/','L1','抱歉','😔'),
    ('like','/laɪk/','L1','喜欢','💗'),
    ('want','/wɒnt/','L1','想要','🤲'),
    ('see','/siː/','L1','看见','👀'),
    ('look','/lʊk/','L1','看','👁️'),
    ('hear','/hɪər/','L1','听见','👂'),
    ('sad','/sæd/','L1','伤心的','😢'),
    ('angry','/ˈæŋ.ɡri/','L1','生气的','😠'),
    ('tired','/ˈtaɪ.əd/','L1','累的','😩'),

    # ---------------- L2 进阶（场景词） ----------------
    ('ambulance','/ˈæm.bjə.ləns/','L2','救护车','🚑','发音联想“俺不能死”→ 救护车救人命（正确拼写 a-m-b-u-l-a-n-c-e）','Call an ambulance now!'),
    ('bicycle','/ˈbaɪ.sɪ.kl/','L2','自行车','🚲','两个轮子(bi=双)的骑车工具','He rides a bicycle to work.'),
    ('forest','/ˈfɒr.ɪst/','L2','森林','🌲','很多树连成片的大森林','They walked into the forest.'),
    ('secret','/ˈsiː.krət/','L2','秘密','🤫','不能说的悄悄话','It is a secret between us.'),
    ('fragile','/ˈfrædʒ.aɪl/','L2','易碎的','🥚','像鸡蛋一样一碰就碎 → 易碎的','The box is fragile.'),
    ('brilliant','/ˈbrɪl.jənt/','L2','聪明的；耀眼的','💡','像灯泡突然亮了 → 聪明的/耀眼的','She is a brilliant student.'),
    ('enormous','/ɪˈnɔː.məs/','L2','巨大的','🐘','比大象还大 → 巨大的','An enormous whale appeared.'),
    ('patient','/ˈpeɪ.ʃənt/','L2','病人；有耐心的','🧘','生病时等你的是病人；能等的是有耐心的','Be patient, it takes time.'),
    ('environment','/ɪnˈvaɪ.rən.mənt/','L2','环境','🌍','我们周围的“环”境','We must protect the environment.'),
    ('consider','/kənˈsɪd.ər/','L2','考虑','🤔','把事放在心里反复想 → 考虑','Please consider my idea.'),
    ('whisper','/ˈwɪs.pər/','L2','耳语；低声说','🤫','凑近耳朵轻轻说 → 耳语','She whispered to me.'),
    ('mountain','/ˈmaʊn.tən/','L2','山','⛰️','高耸入云的大山','We climbed the mountain.'),
    ('library','/ˈlaɪ.brər.i/','L2','图书馆','📚','摆满书、安静看书的地方','I borrow books from the library.'),
    ('restaurant','/ˈres.trɒnt/','L2','餐厅','🍽️','点菜吃饭的地方','We met at a restaurant.'),
    ('umbrella','/ʌmˈbrel.ə/','L2','雨伞','☂️','下雨撑开挡雨的用具','Take an umbrella, it may rain.'),
    ('vegetable','/ˈvedʒ.tə.bəl/','L2','蔬菜','🥦','绿绿的、健康的食物','Eat more vegetables daily.'),
    ('window','/ˈwɪn.dəʊ/','L2','窗户','🪟','墙上透光能看外面的口','Open the window for fresh air.'),
    ('bridge','/brɪdʒ/','L2','桥','🌉','跨过河的通道','We crossed the bridge.'),
    ('telephone','/ˈtel.ɪ.fəʊn/','L2','电话','📞','用来远距离说话的工具','Call me on the telephone.'),
    ('birthday','/ˈbɜːθ.deɪ/','L2','生日','🎂','你来到这天的纪念日','Happy birthday to you!'),
    ('weather','/ˈweð.ər/','L2','天气','🌤️','今天冷热处理况','The weather is nice today.'),
    ('language','/ˈlæŋ.ɡwɪdʒ/','L2','语言','🗣️','人和人沟通的密码','English is a useful language.'),
    ('travel','/ˈtræv.əl/','L2','旅行','✈️','去远方看世界的动作','We love to travel in summer.'),
    ('healthy','/ˈhel.θi/','L2','健康的','💪','身体棒、少生病 → 健康的','Eat well to stay healthy.'),
    # ---- L2 扩充（医疗/动物/形容词/购物/社会） ----
    ('hospital','/ˈhɒs.pɪ.tl/','L2','医院','🏥'),
    ('nurse','/nɜːs/','L2','护士','👩‍⚕️'),
    ('medicine','/ˈmed.ɪ.sɪn/','L2','药','💊'),
    ('sick','/sɪk/','L2','生病的','🤒'),
    ('sky','/skaɪ/','L2','天空','🌌'),
    ('ice','/aɪs/','L2','冰','🧊'),
    ('horse','/hɔːs/','L2','马','🐴'),
    ('cow','/kaʊ/','L2','奶牛','🐄'),
    ('pig','/pɪɡ/','L2','猪','🐷'),
    ('sheep','/ʃiːp/','L2','羊','🐑'),
    ('rabbit','/ˈræb.ɪt/','L2','兔子','🐰'),
    ('monkey','/ˈmʌŋ.ki/','L2','猴子','🐵'),
    ('tiger','/ˈtaɪ.ɡər/','L2','老虎','🐯'),
    ('lion','/ˈlaɪ.ən/','L2','狮子','🦁'),
    ('bear','/beər/','L2','熊','🐻'),
    ('snake','/sneɪk/','L2','蛇','🐍'),
    ('mouse','/maʊs/','L2','老鼠','🐭'),
    ('long','/lɒŋ/','L2','长的','📏'),
    ('short','/ʃɔːt/','L2','短的','✂️'),
    ('tall','/tɔːl/','L2','高的','📏'),
    ('early','/ˈɜːli/','L2','早的','🌅'),
    ('late','/leɪt/','L2','晚的','🌙'),
    ('young','/jʌŋ/','L2','年轻的','🧒'),
    ('busy','/ˈbɪz.i/','L2','忙碌的','🏃'),
    ('free','/friː/','L2','空闲的','🆓'),
    ('buy','/baɪ/','L2','买','🛒'),
    ('sell','/sel/','L2','卖','💱'),
    ('price','/praɪs/','L2','价格','🏷️'),
    ('market','/ˈmɑː.kɪt/','L2','市场','🛒'),
    ('shop','/ʃɒp/','L2','商店','🏪'),
    ('bank','/bæŋk/','L2','银行','🏦'),
    ('post','/pəʊst/','L2','邮政','📮'),
    ('gift','/ɡɪft/','L2','礼物','🎁'),
    ('party','/ˈpɑː.ti/','L2','聚会','🎉'),
    ('holiday','/ˈhɒl.ə.deɪ/','L2','假期','🏖️'),
    ('trip','/trɪp/','L2','旅行','🧳'),
    ('country','/ˈkʌn.tri/','L2','国家','🏳️'),
    ('world','/wɜːld/','L2','世界','🌐'),
    ('culture','/ˈkʌl.tʃər/','L2','文化','🏛️'),
    ('history','/ˈhɪs.tə.ri/','L2','历史','📜'),
    ('future','/ˈfjuː.tʃər/','L2','未来','🔮'),
    ('past','/pɑːst/','L2','过去','⏳'),
    ('airport','/ˈeə.pɔːt/','L2','机场','✈️'),
    ('station','/ˈsteɪ.ʃən/','L2','车站','🚉'),
    ('ticket','/ˈtɪk.ɪt/','L2','票','🎫'),

    # ---------------- L3 高阶（考试核心） ----------------
    ('ambition','/æmˈbɪʃ.ən/','L3','野心；抱负','🚀','心里有火想往上冲 → 野心/抱负','His ambition is to be a pilot.'),
    ('circumstance','/ˈsɜː.kəm.stɑːns/','L3','环境；情况','🔄','站在圆环(circle)里做事 → 周围的情况','Under the circumstance, we waited.'),
    ('dilemma','/dɪˈlem.ə/','L3','困境；两难','😣','两难(di=双)的困境','He faced a real dilemma.'),
    ('elaborate','/ɪˈlæb.ər.ət/','L3','精心制作的；详尽的','🎨','往外(e-)劳动(labor)打磨 → 精心制作的','She made an elaborate plan.'),
    ('phenomenon','/fəˈnɒm.ɪ.nən/','L3','现象','🌈','天上出现的奇景 → 现象','The rainbow is a natural phenomenon.'),
    ('spontaneous','/spɒnˈteɪ.ni.əs/','L3','自发的','✨','自己(spon)冒出来的 → 自发的','A spontaneous trip sounds fun.'),
    ('reluctant','/rɪˈlʌk.tənt/','L3','不情愿的','🛑','不肯往前 → 不情愿的','He was reluctant to leave.'),
    ('tedious','/ˈtiː.di.əs/','L3','冗长乏味的','⏳','时间长到让人烦 → 冗长乏味的','The meeting was tedious.'),
    ('vulnerable','/ˈvʌl.nər.ə.bəl/','L3','脆弱的','🛡️','盾牌挡不住 → 脆弱的','Children are vulnerable.'),
    ('alleviate','/əˈliː.vi.eɪt/','L3','缓解；减轻','🪶','把重量(lev)减轻 → 缓解','This medicine alleviates pain.'),
    ('magnificent','/mæɡˈnɪf.ɪ.sənt/','L3','宏伟的；壮丽的','👑','配得上加冕的 → 宏伟的/壮丽的','What a magnificent view!'),
    ('subsequent','/ˈsʌb.sɪ.kwənt/','L3','随后的','➡️','跟在(sub-)后面的 → 随后的','Subsequent events proved him right.'),
    ('inevitable','/ɪnˈev.ɪ.tə.bəl/','L3','不可避免的','⛓️','躲不掉的 → 必然发生的','Mistakes are inevitable sometimes.'),
    ('comprehensive','/ˌkɒm.prɪˈhen.sɪv/','L3','全面的；综合的','🧩','全抓(com-)理解 → 全面的','We need a comprehensive plan.'),
    ('scrutinize','/ˈskruː.tɪ.naɪz/','L3','仔细审查','🔍','用放大镜看 → 细查','Scrutinize the contract carefully.'),
    ('resilient','/rɪˈzɪl.i.ənt/','L3','有韧性的','🌱','压弯还能弹回 → 坚韧的','She is resilient under pressure.'),
    ('profound','/prəˈfaʊnd/','L3','深刻的','🌊','像深海一样深 → 深刻的','A profound question worth thinking.'),
    ('diligent','/ˈdɪl.ɪ.dʒənt/','L3','勤勉的','📖','努力不偷懒 → 勤奋的','A diligent student studies daily.'),
    ('candidate','/ˈkæn.dɪ.dət/','L3','候选人','🗳️','等着被选的人 → 候选人','He is a candidate for the job.'),
    ('negotiate','/nɪˈɡəʊ.ʃi.eɪt/','L3','谈判；协商','🤝','双方来回谈条件 → 协商','They negotiate a better price.'),
    # ---- L3 扩充（考试核心高频） ----
    ('abandon','/əˈbæn.dən/','L3','放弃','🚪'),
    ('accumulate','/əˈkjuː.mjə.leɪt/','L3','积累','📚'),
    ('adequate','/ˈæd.ɪ.kwət/','L3','足够的','✅'),
    ('anticipate','/ænˈtɪs.ɪ.peɪt/','L3','预期','🔮'),
    ('apparent','/əˈpær.ənt/','L3','明显的','👀'),
    ('approximate','/əˈprɒk.sɪ.mət/','L3','近似的','📏'),
    ('arbitrary','/ˈɑː.bɪ.trər.i/','L3','武断的','🎲'),
    ('assess','/əˈses/','L3','评估','⚖️'),
    ('attribute','/əˈtrɪb.juːt/','L3','归因于','🔗'),
    ('authentic','/ɔːˈθen.tɪk/','L3','真实的','✅'),
    ('bias','/ˈbaɪ.əs/','L3','偏见','⚖️'),
    ('coherent','/kəʊˈhɪə.rənt/','L3','连贯的','🔗'),
    ('comply','/kəmˈplaɪ/','L3','遵守','📋'),
    ('conceive','/kənˈsiːv/','L3','构想','💡'),
    ('consequence','/ˈkɒn.sɪ.kwəns/','L3','后果','⛓️'),
    ('consolidate','/kənˈsɒl.ɪ.deɪt/','L3','巩固','🧱'),
    ('contemporary','/kənˈtem.pər.ər.i/','L3','当代的','🕰️'),
    ('contradict','/ˌkɒn.trəˈdɪkt/','L3','矛盾','⚡'),
    ('deliberate','/dɪˈlɪb.ər.ət/','L3','故意的','🎯'),
    ('diminish','/dɪˈmɪn.ɪʃ/','L3','减少','📉'),
    ('distinct','/dɪˈstɪŋkt/','L3','明显的','🔍'),
    ('elegant','/ˈel.ɪ.ɡənt/','L3','优雅的','💃'),
    ('emphasize','/ˈem.fə.saɪz/','L3','强调','📣'),
    ('enhance','/ɪnˈhɑːns/','L3','提升','⬆️'),
    ('explicit','/ɪkˈsplɪs.ɪt/','L3','明确的','🗣️'),
    ('feasible','/ˈfiː.zə.bəl/','L3','可行的','✅'),
    ('fluctuate','/ˈflʌk.tʃu.eɪt/','L3','波动','📈'),
    ('formulate','/ˈfɔː.mju.leɪt/','L3','制定','📝'),
    ('fundamental','/ˌfʌn.dəˈmen.təl/','L3','基本的','🏗️'),
    ('hypothesis','/haɪˈpɒθ.ə.sɪs/','L3','假设','❓'),
    ('implement','/ˈɪm.plɪ.ment/','L3','实施','🔧'),
    ('integrate','/ˈɪn.tɪ.ɡreɪt/','L3','整合','🧩'),
    ('legitimate','/lɪˈdʒɪt.ɪ.mət/','L3','合法的','⚖️'),
    ('manipulate','/məˈnɪp.jə.leɪt/','L3','操纵','🕹️'),
    ('negligible','/ˈneɡ.lɪ.dʒə.bəl/','L3','可忽略的','🤏'),
    ('notion','/ˈnəʊ.ʃən/','L3','概念','💭'),
    ('objective','/əbˈdʒek.tɪv/','L3','客观的','🎯'),
    ('paradox','/ˈpær.ə.dɒks/','L3','悖论','🌀'),
    ('persist','/pəˈsɪst/','L3','坚持','💪'),
    ('prevalent','/ˈprev.əl.ənt/','L3','普遍的','🌐'),
    ('rational','/ˈræʃ.ən.əl/','L3','理性的','🧠'),
    ('reinforce','/ˌriː.ɪnˈfɔːs/','L3','加强','🛡️'),
    ('subtle','/ˈsʌt.əl/','L3','微妙的','🔍'),
    ('tremendous','/trəˈmen.dəs/','L3','巨大的','🌟'),
    ('unanimous','/juˈnæn.ɪ.məs/','L3','一致的','🤝'),
    ('versatile','/ˈvɜː.sə.taɪl/','L3','多才多艺的','🎨'),
    ('vivid','/ˈvɪv.ɪd/','L3','生动的','🌈'),
]

# 强记忆点词的趣味钩子（与正确拼写视觉分离，绝不诱导错误拼写）
HOOK_MAP = {
    'ambulance':'发音联想“俺不能死”→ 救护车救人命（正确拼写 a-m-b-u-l-a-n-c-e）',
    'bicycle':'两个轮子(bi=双)的骑车工具',
    'fragile':'像鸡蛋一样一碰就碎 → 易碎的',
    'brilliant':'像灯泡突然亮了 → 聪明的/耀眼的',
    'enormous':'比大象还大 → 巨大的',
    'environment':'我们周围的“环”境',
    'circumstance':'站在圆环(circle)里做事 → 周围的情况',
    'dilemma':'两难(di=双)的困境',
    'elaborate':'往外(e-)劳动(labor)打磨 → 精心制作的',
    'spontaneous':'自己(spon)冒出来的 → 自发的',
    'reluctant':'不肯往前 → 不情愿的',
    'tedious':'时间长到让人烦 → 冗长乏味的',
    'vulnerable':'盾牌挡不住 → 脆弱的',
    'alleviate':'把重量(lev)减轻 → 缓解',
    'magnificent':'配得上加冕的 → 宏伟的/壮丽的',
    'subsequent':'跟在(sub-)后面的 → 随后的',
    'inevitable':'躲不掉的 → 必然发生的',
    'comprehensive':'全抓(com-)理解 → 全面的',
    'scrutinize':'用放大镜看 → 细查',
    'resilient':'压弯还能弹回 → 坚韧的',
    'profound':'像深海一样深 → 深刻的',
    'diligent':'努力不偷懒 → 勤奋的',
    'candidate':'等着被选的人 → 候选人',
    'negotiate':'双方来回谈条件 → 协商',
    'patient':'生病时等你的是病人；能等的是有耐心的',
    'consider':'把事放在心里反复想 → 考虑',
    'whisper':'凑近耳朵轻轻说 → 耳语',
    'secret':'不能说的悄悄话',
    'abandon':'a(离开)+band(绑)→ 解开束缚 → 放弃',
    'accumulate':'积累(ac-)到一起 → 越攒越多',
    'adequate':'ad(去)+equ(相等)→ 刚好够 → 足够的',
    'anticipate':'提前(after)抓(cap)住 → 预期',
    'assess':'坐下来细看 → 评估',
    'attribute':'把原因(a-)归给(tribute) → 归因于',
    'comply':'com(一起)+ply(折)→ 折服照做 → 遵守',
    'consequence':'跟着(con-)结果(sequence)→ 后果',
    'consolidate':'一起(con-)变 solid → 巩固',
    'contradict':'contra(反)+dict(说)→ 反着说 → 矛盾',
    'deliberate':'de(下)+liber(秤)→ 掂量后 → 故意的',
    'diminish':'一点点(min)变小 → 减少',
    'emphasize':'em(使)+phase(显)→ 使其显眼 → 强调',
    'enhance':'en(使)+hance(高)→ 抬高 → 提升',
    'implement':'im(进)+ple(满)→ 落实填满 → 实施',
    'integrate':'in(整)+teg(触)→ 触成一体 → 整合',
    'objective':'obj(物)+ive→ 看物体而非主观 → 客观的',
    'persist':'per(始终)+sist(站)→ 一直站着 → 坚持',
    'reinforce':'re(再)+in(入)+force→ 再加力 → 加强',
    'tremendous':'trem(颤抖)→ 大得让人抖 → 巨大的',
}

def generate_hook(term, df, em):
    if term in HOOK_MAP: return HOOK_MAP[term]
    return f'{em} {df} —— 多读多听，记住 {term}'

def generate_example(term, df):
    return f'跟读："{term}" 意思是「{df}」'

def build():
    out = []
    for row in RAW:
        if len(row) == 7:
            term, ph, lv, df, em, hook, ex = row
        elif len(row) == 5:
            term, ph, lv, df, em = row
            hook, ex = '', ''
        else:
            term, ph, lv, df = row
            em, hook, ex = None, '', ''
        if not hook: hook = generate_hook(term, df, em or emoji_of(term))
        if not ex: ex = generate_example(term, df)
        out.append({
            'term': term,
            'phonetic': ph,
            'level': lv,
            'def': df,
            'emoji': em if em else emoji_of(term),
            'hook': hook,
            'example': ex,
        })
    return out

def to_js(words):
    lines = []
    lines.append('// 英语趣学 H5 · 种子词库（MVP 演示，由 tools/gen_words.py 生成）')
    lines.append('// 字段: term 单词, phonetic 音标, level 级别, def 中文释义,')
    lines.append('//       emoji 联想图, hook 记忆口诀(趣味钩子，与正确拼写视觉分离), example 例句')
    lines.append('const WORD_BANK = [')
    for w in words:
        lines.append('  ' + json.dumps(w, ensure_ascii=False) + ',')
    lines.append('];')
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    words = build()
    js = to_js(words)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'js', 'words.js')
    out_path = os.path.abspath(out_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js)
    # 统计分级
    from collections import Counter
    c = Counter(w['level'] for w in words)
    print(f'生成完成: {len(words)} 词 -> {out_path}')
    print('分级统计:', dict(c))
