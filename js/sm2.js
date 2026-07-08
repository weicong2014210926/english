/* SM-2 间隔重复算法（简化实现，与后端 SpacedRepetitionService 对齐）
   字段: easeFactor(难度系数) interval(天) repetitions(连续答对次数) dueDate(下次复习时间戳)
   quality: 0-5  (0=完全不记得, 3=勉强想起, 5=瞬间想起)
*/
const SM2 = {
  // 默认新词初始状态
  fresh() {
    return { easeFactor: 2.5, interval: 0, repetitions: 0, dueDate: Date.now() };
  },

  // 根据作答质量推进调度，返回新的复习状态
  review(card, quality) {
    let { easeFactor = 2.5, interval = 0, repetitions = 0 } = card || SM2.fresh();

    if (quality < 3) {
      // 答错：重置连击，明天再练
      repetitions = 0;
      interval = 1;
    } else {
      if (repetitions === 0) interval = 1;
      else if (repetitions === 1) interval = 6;
      else interval = Math.round(interval * easeFactor);
      repetitions += 1;
    }

    // 难度系数更新公式
    easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
    if (easeFactor < 1.3) easeFactor = 1.3;

    const dueDate = Date.now() + interval * 24 * 60 * 60 * 1000;
    return { easeFactor: +easeFactor.toFixed(2), interval, repetitions, dueDate };
  },

  // 是否到期（可复习）
  isDue(card, now = Date.now()) {
    return !card || card.dueDate <= now;
  }
};

if (typeof module !== 'undefined') module.exports = SM2;
