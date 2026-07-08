<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('review_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('word_id')->constrained()->onDelete('cascade');
            $table->float('ease_factor')->default(2.5);   // SM-2 难度系数
            $table->integer('interval')->default(0);       // 复习间隔（天）
            $table->integer('repetitions')->default(0);    // 连续答对次数
            $table->timestamp('due_date')->index();        // 下次到期时间
            $table->unsignedTinyInteger('last_quality')->nullable();
            $table->boolean('learned')->default(false);
            $table->integer('correct_count')->default(0);
            $table->integer('wrong_count')->default(0);
            $table->timestamps();
            $table->unique(['user_id', 'word_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('review_items');
    }
};
