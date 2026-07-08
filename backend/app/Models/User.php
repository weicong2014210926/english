<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = ['name', 'email', 'password', 'age', 'age_group', 'parent_verified'];

    protected $hidden = ['password', 'remember_token'];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'parent_verified'   => 'boolean',
    ];

    public function stats()        { return $this->hasOne(UserStat::class); }
    public function reviewItems()  { return $this->hasMany(ReviewItem::class); }
    public function checkins()     { return $this->hasMany(Checkin::class); }
}
