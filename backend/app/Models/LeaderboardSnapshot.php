<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LeaderboardSnapshot extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'week_start', 'points', 'rank'];

    public function user() { return $this->belongsTo(User::class); }
}
