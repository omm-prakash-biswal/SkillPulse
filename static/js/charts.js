/*
 * SKILLPULSE — CHART.JS VISUALIZATION ENGINE
 * Configures and renders the civic-cartography charts:
 * 1. Wage Progression Line Chart (Realized vs Baseline Floor)
 * 2. Cohort Conversion Funnel (Bar / Step chart)
 * 3. Provider Pulse Comparison (Grouped Bar Chart)
 * 4. Non-Placement Reasons Diagnostics (Donut Chart)
 */

const SkillPulseCharts = (function() {
  'use strict';

  let wageChartInstance = null;
  let funnelChartInstance = null;
  let providerChartInstance = null;
  let nonPlacementChartInstance = null;

  // Renders the longitudinal wage progression line chart comparing earnings to baseline floor
  function renderWageChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (wageChartInstance) {
      wageChartInstance.destroy();
    }

    wageChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartData.labels || ['Before', '3 months', '6 months', '12 months'],
        datasets: [
          {
            label: 'Median Trainee Wage (₹)',
            data: chartData.trainee_wages || [9800, 12400, 14100, 15800],
            borderColor: '#0E8176',
            backgroundColor: 'rgba(14, 129, 118, 0.12)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#0E8176',
            pointRadius: 5,
            borderWidth: 3
          },
          {
            label: 'Regional Wage Floor (₹)',
            data: chartData.wage_floor || [10500, 10500, 10500, 10500],
            borderColor: '#D69541',
            borderDash: [6, 4],
            fill: false,
            tension: 0,
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' },
              color: '#1E2749'
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `${context.dataset.label}: ₹${context.raw.toLocaleString()}`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            suggestedMin: 8000,
            ticks: {
              callback: function(val) { return `₹${val.toLocaleString()}`; },
              color: '#64748B',
              font: { family: 'Plus Jakarta Sans' }
            },
            grid: { color: '#E2E8F0' }
          },
          x: {
            ticks: { color: '#64748B', font: { family: 'Plus Jakarta Sans', weight: '600' } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Renders the cohort conversion funnel illustrating drop-off and placement yield
  function renderFunnelChart(canvasId, chartData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (funnelChartInstance) {
      funnelChartInstance.destroy();
    }

    funnelChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: chartData.labels || ['Enrolled', 'Trained', 'Certified', 'Placed', 'Retained'],
        datasets: [{
          label: 'Learner Cohort Count',
          data: chartData.counts || [8420, 7820, 6940, 5410, 3698],
          backgroundColor: [
            '#1E2749',
            '#2A3660',
            '#49618B',
            '#0E8176',
            '#14B8A6'
          ],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: function(context) {
                const percentages = chartData.percentages || [100, 92.9, 82.4, 64.3, 44.0];
                return `Conversion Rate: ${percentages[context.dataIndex]}%`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: '#64748B', font: { family: 'Plus Jakarta Sans' } },
            grid: { color: '#E2E8F0' }
          },
          x: {
            ticks: { color: '#1E2749', font: { family: 'Plus Jakarta Sans', weight: '600' } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Renders grouped bar chart benchmarking training providers on placement and retention
  function renderProviderPulseChart(canvasId, providers) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (providerChartInstance) {
      providerChartInstance.destroy();
    }

    const labels = providers ? providers.map(p => `${p.name} (${p.district || ''})`) : ['Saksham (Pune)', 'Jan Disha (Ranchi)', 'Udaan (Jaipur)', 'Navjeevan (Guwahati)'];
    const placementData = providers ? providers.map(p => p.placement) : [78, 73, 69, 62];
    const retentionData = providers ? providers.map(p => p.retention) : [69, 64, 61, 55];

    providerChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Placement Rate (%)',
            data: placementData,
            backgroundColor: '#0E8176',
            borderRadius: 6
          },
          {
            label: '12-Month Retention Rate (%)',
            data: retentionData,
            backgroundColor: '#49618B',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { font: { family: 'Plus Jakarta Sans', size: 12, weight: '600' }, color: '#1E2749' }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: { callback: function(v) { return v + '%'; }, color: '#64748B' },
            grid: { color: '#E2E8F0' }
          },
          x: {
            ticks: { color: '#1E2749', font: { family: 'Plus Jakarta Sans', weight: '600' } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Renders the donut chart displaying root causes for non-placement
  function renderNonPlacementChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (nonPlacementChartInstance) {
      nonPlacementChartInstance.destroy();
    }

    nonPlacementChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels || ['Location / migration', 'Skill mismatch', 'No local demand', 'Family / social', 'Wage expectations'],
        datasets: [{
          data: data.values || [29, 23, 19, 16, 13],
          backgroundColor: [
            '#1E2749',
            '#0E8176',
            '#D69541',
            '#D56F58',
            '#49618B'
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' },
              color: '#1E2749'
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` ${context.label}: ${context.raw}%`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  let skillGapChartInstance = null;

  // Renders horizontal bar chart displaying identified skill gap diagnostics
  function renderSkillGapChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (skillGapChartInstance) {
      skillGapChartInstance.destroy();
    }

    const labels = data && data.labels ? data.labels : ['Practical Hands-on Tools', 'Communication & Spoken English', 'Core Technical Theory', 'Interview Preparedness', 'Digital Workplace Software'];
    const values = data && data.values ? data.values : [38, 27, 18, 11, 6];

    skillGapChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Skill Gap Reports',
          data: values,
          backgroundColor: ['#0E8176', '#1E2749', '#D69541', '#49618B', '#D56F58'],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) { return ` ${ctx.raw} trainees flagged`; }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { color: '#64748B', font: { family: 'Plus Jakarta Sans', size: 10 } },
            grid: { color: '#E2E8F0' }
          },
          y: {
            ticks: { color: '#1E2749', font: { family: 'Plus Jakarta Sans', weight: '600', size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  return {
    renderWageChart: renderWageChart,
    renderFunnelChart: renderFunnelChart,
    renderProviderPulseChart: renderProviderPulseChart,
    renderNonPlacementChart: renderNonPlacementChart,
    renderSkillGapChart: renderSkillGapChart
  };
})();

// Attach globally
window.SkillPulseCharts = SkillPulseCharts;
window.FieldAtlasCharts = SkillPulseCharts;
