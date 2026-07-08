<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('user_stats', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->integer('points')->default(0);          // 总积分
            $table->integer('weekly_points')->default(0);    // 本周积分（排行用）
            $table->integer('streak')->default(0);           // 连续签到
            $table->integer('best_streak')->default(0);
            $table->integer('learned_count')->default(0);    // 已学词数
            $table->integer('quiz_correct')->default(0);
            $table->integer('quiz_wrong')->default(0);
            $table->json('level_done')->nullable();          // {L1:true,...}
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('user_stats');
    }
};
