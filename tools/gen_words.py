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
]

def build():
    out = []
    for term, ph, lv, df, em, hook, ex in RAW:
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
