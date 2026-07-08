<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('words', function (Blueprint $table) {
            $table->id();
            $table->string('term')->unique();
            $table->string('phonetic')->nullable();
            $table->enum('level', ['L1', 'L2', 'L3', 'L4'])->index();
            $table->string('def');                                  // 中文释义（准确）
            $table->string('emoji', 16)->nullable();                // 图像联想（零成本 Emoji）
            $table->text('hook');                                   // 联想记忆故事（趣味须准确）
            $table->text('example')->nullable();                    // 例句
            $table->boolean('accuracy_reviewed')->default(false);  // 内容准确性审核位
            $table->string('source')->nullable();                   // 词源（署名合规）
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('words');
    }
};
