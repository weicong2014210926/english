<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class UserStat extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'points', 'weekly_points', 'streak', 'best_streak',
        'learned_count', 'quiz_correct', 'quiz_wrong', 'level_done',
    ];

    protected $casts = [
        'level_done' => 'array',
    ];

    public function user() { return $this->belongsTo(User::class); }
}
