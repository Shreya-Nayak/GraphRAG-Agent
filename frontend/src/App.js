import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedStates, setCopiedStates] = useState({});
  const [exportingXray, setExportingXray] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post('/generate-tests', {
        query: query.trim()
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate test cases. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, testCaseIndex) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedStates(prev => ({
        ...prev,
        [testCaseIndex]: true
      }));
      setTimeout(() => {
        setCopiedStates(prev => ({
          ...prev,
          [testCaseIndex]: false
        }));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const exportToXray = async () => {
    if (!results?.test_cases?.length) {
      setError('No test cases to export');
      return;
    }

    setExportingXray(true);
    try {
      // Format test cases for Jira Xray export
      const xrayFormat = {
        info: {
          summary: `Test Cases for: ${results.query}`,
          description: `Generated test cases using GraphRAG Agent`,
          version: "1.0",
          user: "graphrag-agent",
          revision: "1",
          startDate: new Date().toISOString().split('T')[0],
          finishDate: new Date().toISOString().split('T')[0],
          testEnvironments: ["Development"]
        },
        tests: results.test_cases.map((testCase, index) => ({
          testKey: `TC-${index + 1}`,
          testType: "Manual",
          summary: testCase.title || `Test Case ${index + 1}`,
          description: testCase.description || '',
          steps: testCase.steps?.map((step, stepIndex) => ({
            action: step.action || step,
            data: step.data || "",
            result: step.expected_result || step.result || ""
          })) || [],
          preconditions: testCase.preconditions || "",
          priority: testCase.priority || "Medium"
        }))
      };

      // Create and download JSON file
      const dataStr = JSON.stringify(xrayFormat, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `xray-test-cases-${new Date().toISOString().split('T')[0]}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      // Show success message
      setError(null);
      
    } catch (err) {
      setError('Failed to export test cases: ' + err.message);
    } finally {
      setExportingXray(false);
    }
  };

  const formatTestCaseForCopy = (testCase) => {
    let formatted = `Test Case: ${testCase.title}\n`;
    formatted += `Summary: ${testCase.summary || 'N/A'}\n`;
    formatted += `Test Type: ${testCase.test_type || 'N/A'}\n`;
    formatted += `Priority: ${testCase.priority || 'N/A'}\n`;
    
    if (testCase.preconditions) {
      formatted += `Preconditions: ${testCase.preconditions}\n`;
    }
    
    formatted += `\nTest Steps:\n`;
    if (testCase.steps && Array.isArray(testCase.steps)) {
      testCase.steps.forEach((step, index) => {
        if (typeof step === 'object') {
          formatted += `${index + 1}. Action: ${step.action}\n`;
          if (step.data) formatted += `   Data: ${step.data}\n`;
          formatted += `   Expected: ${step.expected_result}\n`;
        } else {
          formatted += `${index + 1}. ${step}\n`;
        }
      });
    }
    
    formatted += `\nExpected Result: ${testCase.expected_result}\n`;
    
    if (testCase.test_script) {
      formatted += `\nTest Script:\n${testCase.test_script}\n`;
    }
    
    if (testCase.labels && testCase.labels.length > 0) {
      formatted += `\nLabels: ${testCase.labels.join(', ')}\n`;
    }
    
    if (testCase.components && testCase.components.length > 0) {
      formatted += `Components: ${testCase.components.join(', ')}\n`;
    }
    
    return formatted;
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🧪 GraphRAG Test Generator</h1>
        <p>AI-powered test case generation using knowledge graphs and document analysis</p>
      </header>

      <section className="query-section">
        <form onSubmit={handleSubmit} className="query-form">
          <div className="form-group">
            <label htmlFor="query">
              📝 Describe what you want to test:
            </label>
            <textarea
              id="query"
              className="query-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., 'Login API should handle invalid credentials', 'User registration flow with validation', 'Payment processing with different card types'..."
              rows={4}
            />
          </div>
          <button 
            type="submit" 
            className="submit-btn"
            disabled={loading}
          >
            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                Generating test cases...
              </div>
            ) : (
              '🚀 Generate Test Cases'
            )}
          </button>
        </form>
      </section>

      {error && (
        <div className="error-message">
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      {results && (
        <section className="results-section">
          <div className="results-header">
            <h2>📋 Generated Test Cases</h2>
            <div className="results-actions">
              <span className="test-case-count">
                {results.test_cases?.length || 0} test cases
              </span>
              <button 
                className="export-btn"
                onClick={exportToXray}
                disabled={exportingXray}
              >
                {exportingXray ? '⏳ Exporting...' : '📤 Export to Jira Xray'}
              </button>
            </div>
          </div>

          <div className="query-display">
            <strong>Query:</strong> {results.query}
          </div>

          <div className="test-cases-grid">
            {results.test_cases?.map((testCase, index) => (
              <div key={index} className="test-case-card">
                <div className="test-case-header">
                  <div className="test-case-title">
                    🎯 {testCase.title}
                  </div>
                  <div className="test-case-meta">
                    <span className="test-type">{testCase.test_type || 'generic'}</span>
                    <span className="priority">{testCase.priority || 'medium'}</span>
                  </div>
                </div>

                {testCase.summary && (
                  <div className="test-summary">
                    <strong>📄 Summary:</strong> {testCase.summary}
                  </div>
                )}

                {testCase.preconditions && (
                  <div className="preconditions">
                    <strong>⚙️ Preconditions:</strong> {testCase.preconditions}
                  </div>
                )}

                {testCase.description && (
                  <div className="test-description">
                    <strong>📋 Description:</strong> {testCase.description}
                  </div>
                )}

                {testCase.steps && testCase.steps.length > 0 && (
                  <div className="test-steps-section">
                    <div className="section-label">
                      📝 Test Steps:
                      <button
                        className={`copy-btn ${copiedStates[index] ? 'copied' : ''}`}
                        onClick={() => copyToClipboard(formatTestCaseForCopy(testCase), index)}
                      >
                        {copiedStates[index] ? '✅ Copied!' : '📋 Copy Test Case'}
                      </button>
                    </div>
                    <ol className="test-steps-list">
                      {testCase.steps.map((step, stepIndex) => (
                        <li key={stepIndex} className="test-step">
                          <div className="step-details">
                            <div className="step-action"><strong>Action:</strong> {step.action}</div>
                            {step.data && <div className="step-data"><strong>Data:</strong> {step.data}</div>}
                            <div className="step-expected"><strong>Expected:</strong> {step.expected_result}</div>
                          </div>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {!testCase.steps && (
                  <div className="copy-section">
                    <button
                      className={`copy-btn ${copiedStates[index] ? 'copied' : ''}`}
                      onClick={() => copyToClipboard(formatTestCaseForCopy(testCase), index)}
                    >
                      {copiedStates[index] ? '✅ Copied!' : '📋 Copy Test Case'}
                    </button>
                  </div>
                )}

                {testCase.expected_result && (
                  <div>
                    <div className="section-label">
                      ✅ Expected Result:
                    </div>
                    <div className="expected-result">
                      {testCase.expected_result}
                    </div>
                  </div>
                )}

                {testCase.test_script && (
                  <div className="test-script-section">
                    <div className="section-label">🔧 Test Script:</div>
                    <pre className="test-script">
                      <code>{testCase.test_script}</code>
                    </pre>
                  </div>
                )}

                {(testCase.labels?.length > 0 || testCase.components?.length > 0) && (
                  <div className="test-metadata">
                    {testCase.labels?.length > 0 && (
                      <div className="labels">
                        <strong>🏷️ Labels:</strong> {testCase.labels.join(', ')}
                      </div>
                    )}
                    {testCase.components?.length > 0 && (
                      <div className="components">
                        <strong>🧩 Components:</strong> {testCase.components.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )) || (
              <div className="test-case-card">
                <div className="test-case-title">No test cases generated</div>
                <p>Try refining your query or check if the backend is running properly.</p>
              </div>
            )}
          </div>

          <div className="export-section">
            <h3>📥 Export Options</h3>
            <button 
              className="export-btn"
              onClick={exportToXray}
              disabled={exportingXray || loading}
            >
              {exportingXray ? '📤 Exporting to Xray...' : '📥 Export to Xray (JSON)'}
            </button>
          </div>
        </section>
      )}
    </div>
  );
};

export default App;
