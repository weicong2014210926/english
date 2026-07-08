<?php

use App\Models\Checkin;
use App\Models\LeaderboardSnapshot;
use App\Models\ReviewItem;
use App\Models\UserStat;
use App\Models\Word;
use App\Services\SpacedRepetitionService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| 英语趣学 H5 · API 路由（与前端 js/app.js 契约对齐）
| 鉴权: Laravel Sanctum (Bearer Token)
|--------------------------------------------------------------------------
*/

// 注册（含未成年年龄组判定，用于广告/合规分流）
Route::post('/register', function (Request $r) {
    $r->validate([
        'name'     => 'required|string|max:30',
        'email'    => 'required|email|unique:users',
        'password' => 'required|min:6',
        'age'      => 'nullable|integer|min:1|max:120',
    ]);
    $age   = $r->age;
    $group = $age && $age < 14 ? 'child' : ($age && $age < 18 ? 'teen' : 'adult');

    $user = \App\Models\User::create([
        'name'      => $r->name,
        'email'     => $r->email,
        'password'  => Hash::make($r->password),
        'age'       => $age,
        'age_group' => $group,
    ]);
    $user->stats()->create([]); // 初始化统计行

    return response()->json(['token' => $user->createToken('h5')->plainTextToken, 'age_group' => $group]);
});

// 登录
Route::post('/login', function (Request $r) {
    $r->validate(['email' => 'required|email', 'password' => 'required']);
    $user = \App\Models\User::where('email', $r->email)->first();
    if (! $user || ! Hash::check($r->password, $user->password)) {
        return response()->json(['message' => '账号或密码错误'], 401);
    }
    return response()->json(['token' => $user->createToken('h5')->plainTextToken, 'age_group' => $user->age_group]);
});

Route::middleware('auth:sanctum')->group(function () {

    // 当前用户
    Route::get('/me', fn () => auth()->user()->load('stats'));

    // 关卡概览（每级总数 / 已学）
    Route::get('/levels', function () {
        $uid = auth()->id();
        $levels = ['L1', 'L2', 'L3', 'L4'];
        $data = [];
        foreach ($levels as $lv) {
            $total   = Word::where('level', $lv)->count();
            $learned = ReviewItem::where('user_id', $uid)->where('learned', true)
                ->whereHas('word', fn ($q) => $q->where('level', $lv))->count();
            $data[$lv] = ['total' => $total, 'learned' => $learned, 'due' => 0];
        }
        $data['due_total'] = ReviewItem::where('user_id', $uid)->where('learned', true)
            ->where('due_date', '<=', now())->count();
        return response()->json($data);
    });

    // 开始学习会话：返回词列表（level 或 review）
    Route::post('/session/start', function (Request $r) {
        $r->validate(['mode' => 'required|in:level,review', 'level' => 'nullable|in:L1,L2,L3,L4']);
        if ($r->mode === 'review') {
            $words = SpacedRepetitionService::dueWords(8)->pluck('word');
        } else {
            $learnedIds = ReviewItem::where('user_id', auth()->id())->where('learned', true)->pluck('word_id');
            $words = Word::where('level', $r->level)->whereNotIn('id', $learnedIds)->inRandomOrder()->limit(8)->get();
            if ($words->isEmpty()) $words = Word::where('level', $r->level)->inRandomOrder()->limit(8)->get();
        }
        return response()->json($words->map(fn ($w) => [
            'term' => $w->term, 'phonetic' => $w->phonetic, 'level' => $w->level,
            'def' => $w->def, 'emoji' => $w->emoji, 'hook' => $w->hook, 'example' => $w->example,
        ]));
    });

    // 提交测验结果：推进 SM-2 + 更新积分/成就
    Route::post('/session/submit', function (Request $r) {
        $r->validate(['items' => 'required|array', 'items.*.term' => 'required', 'items.*.learnQuality' => 'required|integer|between:0,5', 'items.*.quizCorrect' => 'required|boolean']);
        $uid  = auth()->id();
        $stat = UserStat::firstOrCreate(['user_id' => $uid]);
        $correct = 0; $earned = 0;

        foreach ($r->items as $it) {
            $word = Word::where('term', $it['term'])->first();
            if (! $word) continue;
            $item = ReviewItem::firstOrCreate(
                ['user_id' => $uid, 'word_id' => $word->id],
                SpacedRepetitionService::fresh()
            );
            $wasLearned = $item->learned;
            SpacedRepetitionService::advance($item, (int) $it['learnQuality'], (bool) $it['quizCorrect']);

            if (! $wasLearned) $stat->increment('learned_count');
            if ($it['quizCorrect']) { $stat->increment('quiz_correct'); $correct++; $earned += 12; $stat->increment('points'); $stat->increment('weekly_points'); }
            else { $stat->increment('quiz_wrong'); $earned += 3; $stat->increment('points'); $stat->increment('weekly_points'); }
        }

        // 排行榜周快照（upsert）
        $weekStart = now()->startOfWeek()->toDateString();
        LeaderboardSnapshot::updateOrCreate(
            ['user_id' => $uid, 'week_start' => $weekStart],
            ['points' => $stat->weekly_points]
        );

        return response()->json([
            'correct' => $correct, 'total' => count($r->items),
            'earned'  => $earned, 'points' => $stat->points,
        ]);
    });

    // 到期复习词
    Route::get('/review/due', fn () => response()->json(
        SpacedRepetitionService::dueWords(20)->map(fn ($ri) => $ri->word)
    ));

    // 每日签到
    Route::post('/checkin', function () {
        $uid = auth()->id();
        $today = now()->toDateString();
        if (Checkin::where('user_id', $uid)->where('checkin_date', $today)->exists()) {
            return response()->json(['message' => '今日已签到', 'streak' => auth()->user()->stats->streak], 200);
        }
        $yest = now()->subDay()->toDateString();
        $prev = Checkin::where('user_id', $uid)->where('checkin_date', $yest)->first();
        $streak = $prev ? $prev->streak + 1 : 1;
        Checkin::create(['user_id' => $uid, 'checkin_date' => $today, 'streak' => $streak, 'points' => 10]);
        $stat = UserStat::firstOrCreate(['user_id' => $uid]);
        $stat->update(['streak' => $streak, 'best_streak' => max($stat->best_streak, $streak)]);
        $stat->increment('points', 10); $stat->increment('weekly_points', 10);
        return response()->json(['streak' => $streak, 'earned' => 10]);
    });

    // 排行榜（本周快照，按积分排序）
    Route::get('/leaderboard', function () {
        $weekStart = now()->startOfWeek()->toDateString();
        return LeaderboardSnapshot::with('user:id,name')
            ->where('week_start', $weekStart)
            ->orderByDesc('points')->limit(50)
            ->get()->map(fn ($s, $i) => ['rank' => $i + 1, 'name' => $s->user->name ?? '匿名', 'points' => $s->points]);
    });
});
