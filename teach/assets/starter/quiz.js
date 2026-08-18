/*
 * quiz.js — the reusable retrieval-check widget every lesson links.
 * Retrieval practice (recalling from memory) is one of the two highest-evidence
 * learning techniques, so a lesson without at least one check is under-built.
 *
 * A quiz is DECLARED in the lesson HTML, not in JS — the markup is the source of truth:
 *
 *   <div class="quiz" data-answer="1"
 *        data-explain="A working set is taken close to failure; warm-ups are tracked separately.">
 *     <p class="q">Which counts as a "set" in this workspace's glossary?</p>
 *     <ul class="options">
 *       <li>A light warm-up round of ten reps</li>
 *       <li>A hard round taken near failure</li>
 *       <li>Any round of any weight</li>
 *     </ul>
 *     <p class="feedback"></p>
 *   </div>
 *
 * data-answer is the 0-based index of the correct <li>. data-explain is shown after
 * the learner commits — win OR lose, because the explanation is where the learning is.
 *
 * Design rule enforced by convention, not code: every option should be roughly the
 * same length and register. Length or formatting tells give the answer away and turn
 * a retrieval check into a spot-the-odd-one-out.
 */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.quiz').forEach((quiz) => {
    const answer  = Number(quiz.dataset.answer);
    const explain = quiz.dataset.explain || '';
    const options = [...quiz.querySelectorAll('.options li')];
    const feedback = quiz.querySelector('.feedback');
    let answered = false;

    options.forEach((li, i) => {
      li.addEventListener('click', () => {
        if (answered) return;
        answered = true;
        options[answer].classList.add('correct');
        if (i !== answer) li.classList.add('wrong');
        const lead = i === answer ? '✓ Right. ' : '✗ Not quite. ';
        feedback.textContent = lead + explain;
      });
    });
  });
});
