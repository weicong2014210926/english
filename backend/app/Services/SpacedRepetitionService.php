<?php

namespace App\Services;

use App\Models\ReviewItem;
use Illuminate\Support\Facades\Auth;

/**
 * SM-2 间隔重复调度服务
 * 与前端 js/sm2.js 算法保持对齐，服务端为权威计算源。
 * quality: 0-5（0=完全不记得，3=勉强想起，5=瞬间想起）
 */
class SpacedRepetitionService
{
    /** 新词初始状态 */
    public static function fresh(): array
    {
        return [
            'ease_factor' => 2.5,
            'interval'    => 0,
            'repetitions' => 0,
            'due_date'    => now(),
        ];
    }

    /** 根据作答质量推进调度，返回新的复习状态 */
    public static function review(array $card, int $quality): array
    {
        $ef      = (float) ($card['ease_factor'] ?? 2.5);
        $interval = (int)   ($card['interval']    ?? 0);
        $rep     = (int)   ($card['repetitions'] ?? 0);

        if ($quality < 3) {
            $rep = 0;
            $interval = 1;
        } else {
            if ($rep === 0)      $interval = 1;
            elseif ($rep === 1)  $interval = 6;
            else                  $interval = (int) round($interval * $ef);
            $rep += 1;
        }

        $ef = $ef + (0.1 - (5 - $quality) * (0.08 + (5 - $quality) * 0.02));
        if ($ef < 1.3) $ef = 1.3;

        return [
            'ease_factor'  => (float) $ef,
            'interval'     => $interval,
            'repetitions'  => $rep,
            'due_date'     => now()->addDays($interval),
            'last_quality' => $quality,
        ];
    }

    /** 取当前用户到期待复习词 */
    public static function dueWords(int $limit = 20)
    {
        return ReviewItem::with('word')
            ->where('user_id', Auth::id())
            ->where('learned', true)
            ->where('due_date', '<=', now())
            ->orderBy('due_date')
            ->limit($limit)
            ->get();
    }

    /** 推进一步：合并学习自评 quality 与测验对错，更新 ReviewItem */
    public static function advance(ReviewItem $item, int $learnQuality, bool $quizCorrect): ReviewItem
    {
        $finalQ = $quizCorrect ? max($learnQuality, 4) : 2; // 测验错则强制低质量
        $next = self::review([
            'ease_factor' => $item->ease_factor,
            'interval'    => $item->interval,
            'repetitions' => $item->repetitions,
        ], $finalQ);

        $item->fill($next);
        $item->learned = true;
        if ($quizCorrect) $item->correct_count++; else $item->wrong_count++;
        $item->save();

        return $item;
    }
}
