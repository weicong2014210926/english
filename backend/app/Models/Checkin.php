<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Checkin extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'checkin_date', 'streak', 'points'];

    public function user() { return $this->belongsTo(User::class); }
}
