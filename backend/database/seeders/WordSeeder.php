<?php

namespace Database\Seeders;

use App\Models\Word;
use Illuminate\Database\Seeder;

/**
 * 词库种子（MVP 演示 36 词，L1-L3）
 * 数据口径：GSL 通用词表 + CET-4（整理），可商用；释义/音频如需商用请接 Wiktionary(CC BY-SA) 并署名。
 * accuracy_reviewed 默认 false —— 上线前需经内容审核流水线置 true。
 */
class WordSeeder extends Seeder
{
    public function run(): void
    {
        $source = 'GSL/CET-4 整理';
        $rows = [
            // ---------------- L1 ----------------
            ['apple', '/ˈæp.əl/', 'L1', '苹果', '🍎', '红红的、咬一口脆甜——🍎 就是苹果', 'I eat an apple every day.'],
            ['cat', '/kæt/', 'L1', '猫', '🐱', '喵星人，会撒娇的小动物', 'The cat is sleeping.'],
            ['dog', '/dɒɡ/', 'L1', '狗', '🐶', '人类最忠诚的朋友', 'A dog is a good friend.'],
            ['book', '/bʊk/', 'L1', '书', '📖', '知识的载体，翻开就有故事', 'I read a book at night.'],
            ['water', '/ˈwɔː.tər/', 'L1', '水', '💧', '生命之源，渴了喝它', 'Please drink more water.'],
            ['sun', '/sʌn/', 'L1', '太阳', '☀️', '白天发光发热的那颗恒星', 'The sun is bright.'],
            ['happy', '/ˈhæp.i/', 'L1', '开心的', '😊', '心里甜丝丝的开心', 'She is happy today.'],
            ['red', '/red/', 'L1', '红色', '🔴', '交通灯里“停”的颜色', 'I like the red apple.'],
            ['eat', '/iːt/', 'L1', '吃', '🍴', '把食物送进嘴里的动作', 'Let us eat lunch.'],
            ['go', '/ɡəʊ/', 'L1', '去；走', '🚶', '迈开腿往前走', 'We go to school.'],
            ['tree', '/triː/', 'L1', '树', '🌳', '大地上的绿色大伞', 'A bird is in the tree.'],
            ['fish', '/fɪʃ/', 'L1', '鱼', '🐟', '在水里游、不用肺呼吸的动物', 'The fish swims fast.'],

            // ---------------- L2 ----------------
            ['ambulance', '/ˈæm.bjə.ləns/', 'L2', '救护车', '🚑', '发音联想“俺不能死”→ 救护车救人命（正确拼写 a-m-b-u-l-a-n-c-e）', 'Call an ambulance now!'],
            ['bicycle', '/ˈbaɪ.sɪ.kl/', 'L2', '自行车', '🚲', '两个轮子(bi=双)的骑车工具', 'He rides a bicycle to work.'],
            ['forest', '/ˈfɒr.ɪst/', 'L2', '森林', '🌲', '很多树连成片的大森林', 'They walked into the forest.'],
            ['secret', '/ˈsiː.krət/', 'L2', '秘密', '🤫', '不能说的悄悄话', 'It is a secret between us.'],
            ['fragile', '/ˈfrædʒ.aɪl/', 'L2', '易碎的', '🥚', '像鸡蛋一样一碰就碎 → 易碎的', 'The box is fragile.'],
            ['brilliant', '/ˈbrɪl.jənt/', 'L2', '聪明的；耀眼的', '💡', '像灯泡突然亮了 → 聪明的/耀眼的', 'She is a brilliant student.'],
            ['enormous', '/ɪˈnɔː.məs/', 'L2', '巨大的', '🐘', '比大象还大 → 巨大的', 'An enormous whale appeared.'],
            ['patient', '/ˈpeɪ.ʃənt/', 'L2', '病人；有耐心的', '🧘', '生病时等你的是病人；能等的是有耐心的', 'Be patient, it takes time.'],
            ['environment', '/ɪnˈvaɪ.rən.mənt/', 'L2', '环境', '🌍', '我们周围的“环”境', 'We must protect the environment.'],
            ['consider', '/kənˈsɪd.ər/', 'L2', '考虑', '🤔', '把事放在心里反复想 → 考虑', 'Please consider my idea.'],
            ['whisper', '/ˈwɪs.pər/', 'L2', '耳语；低声说', '🤫', '凑近耳朵轻轻说 → 耳语', 'She whispered to me.'],
            ['mountain', '/ˈmaʊn.tən/', 'L2', '山', '⛰️', '高耸入云的大山', 'We climbed the mountain.'],

            // ---------------- L3 ----------------
            ['ambition', '/æmˈbɪʃ.ən/', 'L3', '野心；抱负', '🚀', '心里有火想往上冲 → 野心/抱负', 'His ambition is to be a pilot.'],
            ['circumstance', '/ˈsɜː.kəm.stɑːns/', 'L3', '环境；情况', '🔄', '站在圆环(circle)里做事 → 周围的情况', 'Under the circumstance, we waited.'],
            ['dilemma', '/dɪˈlem.ə/', 'L3', '困境；两难', '😣', '两难(di=双)的困境', 'He faced a real dilemma.'],
            ['elaborate', '/ɪˈlæb.ər.ət/', 'L3', '精心制作的；详尽的', '🎨', '往外(e-)劳动(labor)打磨 → 精心制作的', 'She made an elaborate plan.'],
            ['phenomenon', '/fəˈnɒm.ɪ.nən/', 'L3', '现象', '🌈', '天上出现的奇景 → 现象', 'The rainbow is a natural phenomenon.'],
            ['spontaneous', '/spɒnˈteɪ.ni.əs/', 'L3', '自发的', '✨', '自己(spon)冒出来的 → 自发的', 'A spontaneous trip sounds fun.'],
            ['reluctant', '/rɪˈlʌk.tənt/', 'L3', '不情愿的', '🛑', '不肯往前 → 不情愿的', 'He was reluctant to leave.'],
            ['tedious', '/ˈtiː.di.əs/', 'L3', '冗长乏味的', '⏳', '时间长到让人烦 → 冗长乏味的', 'The meeting was tedious.'],
            ['vulnerable', '/ˈvʌl.nər.ə.bəl/', 'L3', '脆弱的', '🛡️', '盾牌挡不住 → 脆弱的', 'Children are vulnerable.'],
            ['alleviate', '/əˈliː.vi.eɪt/', 'L3', '缓解；减轻', '🪶', '把重量(lev)减轻 → 缓解', 'This medicine alleviates pain.'],
            ['magnificent', '/mæɡˈnɪf.ɪ.sənt/', 'L3', '宏伟的；壮丽的', '👑', '配得上加冕的 → 宏伟的/壮丽的', 'What a magnificent view!'],
            ['subsequent', '/ˈsʌb.sɪ.kwənt/', 'L3', '随后的', '➡️', '跟在(sub-)后面的 → 随后的', 'Subsequent events proved him right.'],
        ];

        foreach ($rows as [$term, $phonetic, $level, $def, $emoji, $hook, $example]) {
            Word::updateOrCreate(
                ['term' => $term],
                compact('phonetic', 'level', 'def', 'emoji', 'hook', 'example') + [
                    'accuracy_reviewed' => false,
                    'source' => $source,
                ]
            );
        }
    }
}
