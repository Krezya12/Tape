/**
 * PDP Academy LMS — Charts Module
 * Uses Chart.js from CDN (loaded in HTML pages)
 */

(function () {
    'use strict';

    // Chart color palette aligned to design system
    const COLORS = {
        primary: '#16A34A',
        primaryL: '#22C55E',
        accent: '#F59E0B',
        accentL: '#FCD34D',
        blue: '#3B82F6',
        blueL: '#60A5FA',
        red: '#EF4444',
        muted: '#94A3B8',
        grid: 'rgba(226,232,240,0.6)',
        gridDark: 'rgba(30,46,72,0.8)',
    };

    function isDark() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    }

    function gridColor() {
        return isDark() ? COLORS.gridDark : COLORS.grid;
    }

    function textColor() {
        return isDark() ? '#94A3B8' : '#64748B';
    }

    function cardBg() {
        return isDark() ? '#131E30' : '#FFFFFF';
    }

    const baseFont = {
        family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif",
        size: 12,
        weight: '500',
    };

    const baseDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {display: false},
            tooltip: {
                backgroundColor: isDark() ? '#1E2E48' : '#0F172A',
                titleColor: '#F1F5F9',
                bodyColor: '#94A3B8',
                borderColor: isDark() ? '#2A3F60' : '#1E293B',
                borderWidth: 1,
                padding: 10,
                cornerRadius: 8,
                titleFont: {...baseFont, weight: '600', size: 13},
                bodyFont: {...baseFont, size: 12},
            },
        },
        scales: {
            x: {
                grid: {color: gridColor(), drawBorder: false},
                ticks: {color: textColor(), font: baseFont},
                border: {display: false},
            },
            y: {
                grid: {color: gridColor(), drawBorder: false},
                ticks: {color: textColor(), font: baseFont},
                border: {display: false},
            },
        },
    };

    /* ─── Attendance Line Chart ──────────────────────── */
    window.renderAttendanceChart = function (canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];
        const data = [88, 92, 85, 95, 90, 97, 93, 88, 96];

        return new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    data,
                    borderColor: COLORS.primary,
                    backgroundColor: ctx => {
                        const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height);
                        g.addColorStop(0, isDark() ? 'rgba(34,197,94,0.25)' : 'rgba(22,163,74,0.15)');
                        g.addColorStop(1, 'rgba(22,163,74,0)');
                        return g;
                    },
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.45,
                    pointBackgroundColor: COLORS.primary,
                    pointBorderColor: cardBg(),
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }],
            },
            options: {
                ...baseDefaults,
                plugins: {
                    ...baseDefaults.plugins,
                    tooltip: {
                        ...baseDefaults.plugins.tooltip,
                        callbacks: {label: ctx => `Attendance: ${ctx.raw}%`},
                    },
                },
                scales: {
                    ...baseDefaults.scales,
                    y: {
                        ...baseDefaults.scales.y,
                        min: 70, max: 100,
                        ticks: {...baseDefaults.scales.y.ticks, callback: v => v + '%'},
                    },
                },
            },
        });
    };

    /* ─── Grades Bar Chart ───────────────────────────── */
    window.renderGradesChart = function (canvasId, dynamicLabels, dynamicHw, dynamicCw) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        // Если данные из Django не дошли, используем дефолтные заглушки Клода
        const labels = dynamicLabels || ['Module 1', 'Module 2', 'Module 3', 'Module 4', 'Module 5', 'Module 6'];
        const hw = dynamicHw;
        const cw = dynamicCw;

        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Homework',
                        data: hw,
                        backgroundColor: isDark() ? 'rgba(34,197,94,0.7)' : 'rgba(22,163,74,0.75)',
                        borderRadius: 6,
                        borderSkipped: false,
                    },
                    {
                        label: 'Classwork',
                        data: cw,
                        backgroundColor: isDark() ? 'rgba(59,130,246,0.55)' : 'rgba(59,130,246,0.55)',
                        borderRadius: 6,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                ...baseDefaults,
                plugins: {
                    ...baseDefaults.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: textColor(),
                            font: baseFont,
                            boxWidth: 10,
                            boxHeight: 10,
                            borderRadius: 3,
                            useBorderRadius: true,
                            padding: 16
                        },
                    },
                    tooltip: {...baseDefaults.plugins.tooltip, mode: 'index', intersect: false},
                },
                scales: {
                    ...baseDefaults.scales,
                    y: {
                        ...baseDefaults.scales.y,
                        min: 0,
                        max: 20,
                        ticks: {...baseDefaults.scales.y.ticks, stepSize: 5}
                    },
                },
            },
        });
    };


    /* ─── Module Progress Doughnut ───────────────────── */
    window.renderProgressDoughnut = function (canvasId, value, color) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        const c = color || COLORS.primary;

        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, 100 - value],
                    backgroundColor: [c, isDark() ? '#1E2E48' : '#F1F5F9'],
                    borderWidth: 0,
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    legend: {display: false},
                    tooltip: {enabled: false},
                },
                animation: {animateRotate: true, duration: 1000},
            },
        });
    };

    /* ─── Multi-metric Area Chart (Statistics page) ──── */
    window.renderStatsChart = function (canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'];
        const perf = [72, 78, 75, 83, 88, 85, 91, 87];
        const att = [90, 88, 95, 92, 97, 93, 96, 95];
        const hw = [65, 70, 80, 75, 85, 80, 88, 80];

        const mkDataset = (label, data, color) => ({
            label,
            data,
            borderColor: color,
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.45,
            pointBackgroundColor: color,
            pointBorderColor: cardBg(),
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
        });

        return new Chart(canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    mkDataset('Performance', perf, COLORS.primary),
                    mkDataset('Attendance', att, COLORS.blue),
                    mkDataset('Homework', hw, COLORS.accent),
                ],
            },
            options: {
                ...baseDefaults,
                interaction: {mode: 'index', intersect: false},
                plugins: {
                    ...baseDefaults.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: textColor(),
                            font: baseFont,
                            boxWidth: 10,
                            boxHeight: 10,
                            borderRadius: 3,
                            useBorderRadius: true,
                            padding: 16
                        },
                    },
                    tooltip: {
                        ...baseDefaults.plugins.tooltip,
                        callbacks: {label: ctx => `${ctx.dataset.label}: ${ctx.raw}%`}
                    },
                },
                scales: {
                    ...baseDefaults.scales,
                    y: {
                        ...baseDefaults.scales.y,
                        min: 50,
                        max: 100,
                        ticks: {...baseDefaults.scales.y.ticks, callback: v => v + '%'}
                    },
                },
            },
        });
    };

    /* ─── Admin Overview Bar Chart ───────────────────── */
    window.renderAdminOverviewChart = function (canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        const labels = ['P38', 'P41', 'J12', 'P45', 'F09', 'R22', 'J15', 'P50'];
        const avgScore = [87, 92, 78, 85, 90, 82, 88, 76];
        const attendance = [94, 89, 96, 91, 88, 95, 93, 85];

        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Avg Score',
                        data: avgScore,
                        backgroundColor: isDark() ? 'rgba(34,197,94,0.7)' : 'rgba(22,163,74,0.75)',
                        borderRadius: 5,
                        borderSkipped: false,
                    },
                    {
                        label: 'Attendance',
                        data: attendance,
                        backgroundColor: isDark() ? 'rgba(59,130,246,0.55)' : 'rgba(59,130,246,0.55)',
                        borderRadius: 5,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                ...baseDefaults,
                plugins: {
                    ...baseDefaults.plugins,
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: textColor(),
                            font: baseFont,
                            boxWidth: 10,
                            boxHeight: 10,
                            borderRadius: 3,
                            useBorderRadius: true,
                            padding: 16
                        },
                    },
                    tooltip: {...baseDefaults.plugins.tooltip, mode: 'index', intersect: false},
                },
                scales: {
                    ...baseDefaults.scales,
                    y: {
                        ...baseDefaults.scales.y,
                        min: 60,
                        max: 100,
                        ticks: {...baseDefaults.scales.y.ticks, callback: v => v + '%'}
                    },
                },
            },
        });
    };

    /* ─── Payment Doughnut ───────────────────────────── */
    window.renderPaymentChart = function (canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !window.Chart) return;

        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Paid', 'Pending', 'Overdue'],
                datasets: [{
                    data: [226, 12, 7],
                    backgroundColor: [COLORS.primary, COLORS.accent, COLORS.red],
                    borderWidth: 2,
                    borderColor: cardBg(),
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: textColor(),
                            font: baseFont,
                            padding: 16,
                            boxWidth: 10,
                            boxHeight: 10,
                            borderRadius: 3,
                            useBorderRadius: true
                        },
                    },
                    tooltip: {...baseDefaults.plugins.tooltip},
                },
            },
        });
    };

    /* ─── Update all charts on theme change ──────────── */
    window.updateChartsTheme = function () {
        if (!window.Chart) return;
        Object.values(Chart.instances || {}).forEach(chart => {
            try {
                chart.update('none');
            } catch (e) {
            }
        });
    };

    /* ─── Auto-init ─────────────────────────────────── */
    function init() {
        if (!window.Chart) return;
        if (document.getElementById('attendanceChart')) renderAttendanceChart('attendanceChart');
        if (document.getElementById('gradesChart')) renderGradesChart('gradesChart');
        if (document.getElementById('statsChart')) renderStatsChart('statsChart');
        if (document.getElementById('adminOverviewChart')) renderAdminOverviewChart('adminOverviewChart');
        if (document.getElementById('paymentChart')) renderPaymentChart('paymentChart');

        // Doughnut rings on stats page
        ['perfDoughnut', 'attDoughnut', 'hwDoughnut'].forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const pct = parseInt(el.dataset.value || 0);
            const color = el.dataset.color || COLORS.primary;
            renderProgressDoughnut(id, pct, color);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
