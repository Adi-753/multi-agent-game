const API_BASE = 'http://localhost:8000';

let currentPlan = null;
let executionInterval = null;

const generatePlanBtn = document.getElementById('generatePlanBtn');
const executeTestsBtn = document.getElementById('executeTestsBtn');
const viewReportsBtn = document.getElementById('viewReportsBtn');
const statusMessage = document.getElementById('statusMessage');
const progressBar = document.getElementById('progressBar');
const currentTestDiv = document.getElementById('currentTest');
const testPlanSection = document.getElementById('testPlanSection');
const resultsSection = document.getElementById('resultsSection');
const reportsSection = document.getElementById('reportsSection');

generatePlanBtn.addEventListener('click', generateTestPlan);
executeTestsBtn.addEventListener('click', executeTests);
viewReportsBtn.addEventListener('click', viewReports);
async function generateTestPlan() {
    try {
        updateStatus('Generating test plan...', 'info');
        generatePlanBtn.disabled = true;
        
        const response = await fetch(`${API_BASE}/api/generate-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to generate test plan');
        
        const data = await response.json();
        currentPlan = data.plan;
        
        displayTestPlan(currentPlan);
        updateStatus('Test plan generated successfully!', 'success');
        executeTestsBtn.disabled = false;
        
    } catch (error) {
        updateStatus(`Error: ${error.message}`, 'error');
    } finally {
        generatePlanBtn.disabled = false;
    }
}

async function executeTests() {
    try {
        updateStatus('Starting test execution...', 'info');
        executeTestsBtn.disabled = true;
        progressBar.style.display = 'block';
        
        const response = await fetch(`${API_BASE}/api/execute-tests`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to start test execution');
        
        executionInterval = setInterval(checkExecutionStatus, 1000);
        
    } catch (error) {
        updateStatus(`Error: ${error.message}`, 'error');
        executeTestsBtn.disabled = false;
        progressBar.style.display = 'none';
    }
}

async function checkExecutionStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/execution-status`);
        const status = await response.json();
        
        updateProgress(status.progress || 0);
        
        if (status.current_test) {
            currentTestDiv.textContent = `Current test: ${status.current_test}`;
        }
        
        if (status.status === 'completed') {
            clearInterval(executionInterval);
            updateStatus('Test execution completed!', 'success');
            executeTestsBtn.disabled = false;
            progressBar.style.display = 'none';
            currentTestDiv.textContent = '';
            
            if (status.report_id) {
                await loadReport(status.report_id);
            }
            
        } else if (status.status === 'error') {
            clearInterval(executionInterval);
            updateStatus(`Error: ${status.error}`, 'error');
            executeTestsBtn.disabled = false;
            progressBar.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

async function loadReport(reportId) {
    try {
        const response = await fetch(`${API_BASE}/api/reports/${reportId}`);
        const report = await response.json();
        
        displayResults(report);
        
    } catch (error) {
        updateStatus(`Error loading report: ${error.message}`, 'error');
    }
}

async function viewReports() {
    try {
        updateStatus('Loading reports...', 'info');
        hideAllSections();
        
        const response = await fetch(`${API_BASE}/api/reports`);
        const data = await response.json();
        
        displayReportsList(data.reports);
        reportsSection.style.display = 'block';
        updateStatus('Reports loaded successfully', 'success');
        
    } catch (error) {
        updateStatus(`Error: ${error.message}`, 'error');
    }
}

function displayTestPlan(plan) {
    hideAllSections();
    testPlanSection.style.display = 'block';
    
    document.getElementById('totalTests').textContent = plan.total_cases;
    
    const testList = document.getElementById('testList');
    testList.innerHTML = '';
    
    plan.test_cases.forEach((test, index) => {
        const isTop10 = index < 10;
        const testItem = createTestItem(test, isTop10);
        testList.appendChild(testItem);
    });
}

function createTestItem(test, isTop10) {
    const div = document.createElement('div');
    div.className = `test-item ${isTop10 ? 'top-10' : ''}`;
    
    div.innerHTML = `
        <div class="test-header">
            <div class="test-name">${test.rank}. ${test.name}</div>
            <span class="test-priority priority-${test.priority.toLowerCase()}">${test.priority}</span>
        </div>
        <div class="test-meta">
            <span>Category: ${test.category}</span>
            <span>Duration: ${test.estimated_duration}s</span>
            <span>Score: ${test.score.toFixed(2)}</span>
            ${isTop10 ? '<span style="color: #48bb78; font-weight: 600;">✓ Selected for execution</span>' : ''}
        </div>
    `;
    
    return div;
}

function displayResults(report) {
    hideAllSections();
    resultsSection.style.display = 'block';
    
    const summary = report.summary;
    const summaryHtml = `
        <div class="result-card pass">
            <div class="number">${summary.passed}</div>
            <div class="label">Passed</div>
        </div>
        <div class="result-card fail">
            <div class="number">${summary.failed}</div>
            <div class="label">Failed</div>
        </div>
        <div class="result-card warning">
            <div class="number">${summary.flaky}</div>
            <div class="label">Flaky</div>
        </div>
        <div class="result-card">
            <div class="number">${summary.pass_rate}%</div>
            <div class="label">Pass Rate</div>
        </div>
    `;
    
    document.getElementById('resultsSummary').innerHTML = summaryHtml;
    
    const detailsDiv = document.getElementById('resultsDetails');
    detailsDiv.innerHTML = '';
    
    report.test_results.forEach(result => {
        const resultItem = createResultItem(result);
        detailsDiv.appendChild(resultItem);
    });
    
    if (report.recommendations && report.recommendations.length > 0) {
        const recoDiv = document.createElement('div');
        recoDiv.className = 'triage-notes';
        recoDiv.innerHTML = `
            <h4>Recommendations</h4>
            <ul>
                ${report.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
        detailsDiv.appendChild(recoDiv);
    }
}

function createResultItem(result) {
    const div = document.createElement('div');
    div.className = 'result-item';
    
    const verdictClass = `verdict-${result.verdict.toLowerCase().replace('_', '-')}`;
    
    let artifactsHtml = '';
    if (result.evidence && result.evidence.key_screenshots) {
        artifactsHtml = `
            <div class="artifacts-preview">
                ${result.evidence.key_screenshots.map((screenshot, idx) => 
                    `<a href="/${screenshot}" target="_blank" class="artifact-link">Screenshot ${idx + 1}</a>`
                ).join('')}
            </div>
        `;
    }
    
    div.innerHTML = `
        <div class="result-verdict ${verdictClass}">${result.verdict}</div>
        <h3>${result.test_name}</h3>
        
        <div class="test-meta">
            <span>Reproducibility: ${(result.reproducibility_score * 100).toFixed(0)}%</span>
            <span>Confidence: ${(result.consensus.confidence * 100).toFixed(0)}%</span>
            <span>Executions: ${result.consensus.success_count}/${result.consensus.total_count}</span>
        </div>
        
        ${result.triage_notes && result.triage_notes.length > 0 ? `
            <div class="triage-notes">
                <h4>Triage Notes</h4>
                <ul>
                    ${result.triage_notes.map(note => `<li>${note}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${artifactsHtml}
    `;
    
    return div;
}

function displayReportsList(reports) {
    const reportsList = document.getElementById('reportsList');
    reportsList.innerHTML = '';
    
    if (reports.length === 0) {
        reportsList.innerHTML = '<p>No reports available yet.</p>';
        return;
    }
    
    reports.reverse().forEach(reportId => {
        const reportItem = document.createElement('div');
        reportItem.className = 'report-item';
        reportItem.onclick = () => loadAndDisplayReport(reportId);
        
        const dateMatch = reportId.match(/(\d{8})_(\d{6})/);
        let dateStr = 'Unknown date';
        if (dateMatch) {
            const year = dateMatch[1].substr(0, 4);
            const month = dateMatch[1].substr(4, 2);
            const day = dateMatch[1].substr(6, 2);
            const hour = dateMatch[2].substr(0, 2);
            const minute = dateMatch[2].substr(2, 2);
            dateStr = `${year}-${month}-${day} ${hour}:${minute}`;
        }
        
        reportItem.innerHTML = `
            <div class="report-header">
                <span class="report-id">${reportId}</span>
                <span class="report-date">${dateStr}</span>
            </div>
            <div class="report-stats">
                <div class="stat-item">
                    <span class="stat-label">Click to view report details</span>
                </div>
            </div>
        `;
        
        reportsList.appendChild(reportItem);
    });
}

async function loadAndDisplayReport(reportId) {
    try {
        updateStatus('Loading report...', 'info');
        await loadReport(reportId);
    } catch (error) {
        updateStatus(`Error loading report: ${error.message}`, 'error');
    }
}

function updateStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
}

function updateProgress(percentage) {
    const progressFill = document.querySelector('.progress-fill');
    progressFill.style.width = `${percentage}%`;
    progressFill.textContent = `${Math.round(percentage)}%`;
}

function hideAllSections() {
    testPlanSection.style.display = 'none';
    resultsSection.style.display = 'none';
    reportsSection.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    updateStatus('Ready to start testing...', 'info');
});