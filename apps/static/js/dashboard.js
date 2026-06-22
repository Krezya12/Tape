/**
 * PDP Academy LMS — Dashboard Module
 * Handles dashboard-specific logic: stat cards, activity feed, role detection
 */

(function () {
  'use strict';

  /* ─── Role Detection ────────────────────────────── */
  const role = document.querySelector('[data-user-role]')?.dataset.userRole || 'student';

  /* ─── Stat Card Counter Animation ──────────────── */
  function animateStatCards() {
    document.querySelectorAll('.stat-value[data-count]').forEach(el => {
      const target   = parseFloat(el.dataset.count);
      const suffix   = el.dataset.suffix || '';
      const prefix   = el.dataset.prefix || '';
      const duration = 1400;
      const start    = performance.now();
      const isFloat  = !Number.isInteger(target);

      const tick = (t) => {
        const elapsed  = t - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased    = 1 - Math.pow(1 - progress, 4);
        const value    = target * eased;
        el.textContent = prefix + (isFloat ? value.toFixed(1) : Math.round(value)) + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }

  /* ─── Activity Feed (Simulated) ─────────────────── */
  const ACTIVITY_TEMPLATES = {
    admin: [
      { icon: '👤', text: 'New student registered: <strong>Doniyor Yusupov</strong>', time: '2 min ago', color: 'blue' },
      { icon: '💳', text: 'Payment confirmed — Group <strong>P38</strong>, Module 3', time: '15 min ago', color: 'green' },
      { icon: '🏫', text: 'Group <strong>J15</strong> created — 22 students enrolled', time: '1 hr ago', color: 'green' },
      { icon: '🔑', text: 'Password reset for <strong>teacher@pdp.uz</strong>', time: '2 hr ago', color: 'neutral' },
      { icon: '📊', text: 'Monthly report generated for Q2 2025', time: '3 hr ago', color: 'blue' },
      { icon: '⚠️', text: 'Overdue payment — 7 students, Module 4', time: '5 hr ago', color: 'gold' },
    ],
    teacher: [
      { icon: '📝', text: '<strong>Alex Kim</strong> submitted Homework — Module 3 Lesson 7', time: '5 min ago', color: 'blue' },
      { icon: '✅', text: 'Grades updated for Group <strong>P38</strong> — Classwork', time: '30 min ago', color: 'green' },
      { icon: '📖', text: 'Lesson 8 materials uploaded — Module 3', time: '1 hr ago', color: 'green' },
      { icon: '👀', text: '<strong>Timur R.</strong> viewed lesson recording 3 times', time: '2 hr ago', color: 'neutral' },
      { icon: '❓', text: 'New question from <strong>Maria Chen</strong> on Homework', time: '3 hr ago', color: 'blue' },
    ],
    student: [
      { icon: '📊', text: 'Homework graded: <strong>18/20</strong> — Module 3 Lesson 6', time: '1 hr ago', color: 'green' },
      { icon: '📖', text: 'New lesson available: <strong>Module 3 — Lesson 8</strong>', time: '3 hr ago', color: 'blue' },
      { icon: '🏆', text: 'Leaderboard update — you moved up to <strong>#9</strong>!', time: '5 hr ago', color: 'gold' },
      { icon: '💳', text: 'Module 3 payment confirmed', time: '1 day ago', color: 'green' },
    ],
    parent: [
      { icon: '📊', text: "<strong>Alex's</strong> homework graded: 18/20 — Lesson 6", time: '1 hr ago', color: 'green' },
      { icon: '📅', text: '<strong>Alex</strong> attended today\'s lesson ✓', time: '4 hr ago', color: 'green' },
      { icon: '💳', text: 'Module 3 payment received — thank you!', time: '2 days ago', color: 'green' },
      { icon: '📝', text: "Teacher's note on Alex: excellent progress in algorithms", time: '3 days ago', color: 'blue' },
    ],
  };

  function renderActivityFeed(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const items = ACTIVITY_TEMPLATES[role] || ACTIVITY_TEMPLATES.admin;
    container.innerHTML = items.map(item => `
      <div class="activity-item">
        <div class="activity-icon bg-${item.color}">${item.icon}</div>
        <div class="activity-content">
          <p class="activity-text">${item.text}</p>
          <span class="activity-time">${item.time}</span>
        </div>
      </div>
    `).join('');
  }

  /* ─── Quick Actions Tooltip ─────────────────────── */
  function initQuickActions() {
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const messages = {
          'add-user':      'Opening Add User form…',
          'add-group':     'Opening Create Group…',
          'add-lesson':    'Opening Lesson creator…',
          'grade-journal': 'Opening Grade Journal…',
          'add-homework':  'Opening Homework assignment…',
          'view-report':   'Generating report…',
        };
        if (messages[action] && window.showToast) {
          window.showToast(messages[action], 'info', 2000);
        }
      });
    });
  }

  /* ─── Progress Update (student) ─────────────────── */
  function initStudentProgress() {
    const bar = document.querySelector('.module-progress .progress-bar');
    if (!bar) return;
    const pct = parseFloat(bar.dataset.progress || '0');
    setTimeout(() => { bar.style.width = pct + '%'; }, 300);
  }

  /* ─── Sortable Table Columns ────────────────────── */
  function initSortableHeaders() {
    document.querySelectorAll('th.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const table  = th.closest('table');
        const colIdx = Array.from(th.parentElement.children).indexOf(th);
        const rows   = Array.from(table.querySelectorAll('tbody tr'));
        const asc    = th.dataset.sort !== 'asc';

        table.querySelectorAll('th.sortable').forEach(t => {
          t.dataset.sort = '';
          t.querySelector('.sort-icon') && (t.querySelector('.sort-icon').textContent = '↕');
        });

        rows.sort((a, b) => {
          const aVal = a.cells[colIdx]?.textContent.trim() || '';
          const bVal = b.cells[colIdx]?.textContent.trim() || '';
          const num  = !isNaN(parseFloat(aVal)) && !isNaN(parseFloat(bVal));
          if (num) return asc ? parseFloat(aVal) - parseFloat(bVal) : parseFloat(bVal) - parseFloat(aVal);
          return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        });

        rows.forEach(r => table.querySelector('tbody').appendChild(r));
        th.dataset.sort = asc ? 'asc' : 'desc';
        const icon = th.querySelector('.sort-icon');
        if (icon) icon.textContent = asc ? '↑' : '↓';
      });
    });
  }

  /* ─── Dashboard Init ────────────────────────────── */
  function init() {
    animateStatCards();
    renderActivityFeed('activityFeed');
    initQuickActions();
    initStudentProgress();
    initSortableHeaders();

    // Render charts (charts.js must be loaded)
    setTimeout(() => {
      if (window.Chart) {
        if (document.getElementById('adminOverviewChart')) window.renderAdminOverviewChart('adminOverviewChart');
        if (document.getElementById('attendanceChart'))    window.renderAttendanceChart('attendanceChart');
        if (document.getElementById('gradesChart'))        window.renderGradesChart('gradesChart');
        if (document.getElementById('statsChart'))         window.renderStatsChart('statsChart');
        if (document.getElementById('paymentChart'))       window.renderPaymentChart('paymentChart');
        ['perfDoughnut','attDoughnut','hwDoughnut'].forEach(id => {
          const el = document.getElementById(id);
          if (!el) return;
          window.renderProgressDoughnut(id, +el.dataset.value, el.dataset.color);
        });
      }
    }, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Activity feed styles (injected once)
  const activityStyles = `
    .activity-item{display:flex;align-items:flex-start;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)}
    .activity-item:last-child{border-bottom:none}
    .activity-icon{width:36px;height:36px;border-radius:var(--r-full);display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0}
    .activity-icon.bg-green{background:var(--jade-100)}
    .activity-icon.bg-blue{background:var(--blue-100)}
    .activity-icon.bg-gold{background:var(--gold-100)}
    .activity-icon.bg-neutral{background:var(--ink-100)}
    .activity-content{flex:1;min-width:0}
    .activity-text{font-size:.875rem;color:var(--text-secondary);line-height:1.5}
    .activity-text strong{color:var(--text-primary);font-weight:600}
    .activity-time{font-size:.75rem;color:var(--text-muted);margin-top:3px;display:block}
    [data-theme=dark] .activity-icon.bg-green{background:rgba(34,197,94,.12)}
    [data-theme=dark] .activity-icon.bg-blue{background:rgba(59,130,246,.12)}
    [data-theme=dark] .activity-icon.bg-gold{background:rgba(251,191,36,.12)}
    [data-theme=dark] .activity-icon.bg-neutral{background:rgba(100,116,139,.12)}
  `;
  if (!document.getElementById('dashboardStyles')) {
    const style = document.createElement('style');
    style.id = 'dashboardStyles';
    style.textContent = activityStyles;
    document.head.appendChild(style);
  }

})();
