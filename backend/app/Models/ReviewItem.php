<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ReviewItem extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id', 'word_id', 'ease_factor', 'interval', 'repetitions',
        'due_date', 'last_quality', 'learned', 'correct_count', 'wrong_count',
    ];

    protected $casts = [
        'learned'  => 'boolean',
        'due_date' => 'datetime',
    ];

    public function user() { return $this->belongsTo(User::class); }
    public function word() { return $this->belongsTo(Word::class); }
}
