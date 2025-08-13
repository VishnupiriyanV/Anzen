import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, GitBranch, AlertTriangle, Clock, CheckCircle, ExternalLink, FileText, Shield, RefreshCw } from 'lucide-react';

// Mock vulnerability data
const mockVulnerabilities = [
  {
    id: '1',
    severity: 'high',
    title: 'SQL Injection Vulnerability',
    description: 'Potential SQL injection found in user input handling',
    file: 'src/database/queries.js',
    line: 45,
    cve: 'CVE-2024-1234',
    remediation: 'Use parameterized queries or prepared statements to prevent SQL injection attacks. Replace direct string concatenation with parameter binding.',
    example: `// Vulnerable code:
const query = "SELECT * FROM users WHERE id = '" + userId + "'";

// Fixed code:
const query = "SELECT * FROM users WHERE id = ?";
db.query(query, [userId]);`
  },
  {
    id: '2',
    severity: 'high',
    title: 'Cross-Site Scripting (XSS)',
    description: 'Reflected XSS vulnerability in search functionality',
    file: 'src/components/SearchResults.jsx',
    line: 28,
    cve: 'CVE-2024-5678',
    remediation: 'Sanitize user input before displaying it in the DOM. Use proper encoding for output in different contexts.',
    example: `// Vulnerable code:
element.innerHTML = userInput;

// Fixed code:
element.textContent = userInput;
// or use a sanitization library like DOMPurify`
  },
  {
    id: '3',
    severity: 'medium',
    title: 'Insecure Randomness',
    description: 'Using Math.random() for security-sensitive operations',
    file: 'src/utils/token.js',
    line: 12,
    cve: null,
    remediation: 'Use cryptographically secure random number generation for tokens and sensitive operations.',
    example: `// Vulnerable code:
const token = Math.random().toString(36);

// Fixed code:
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');`
  },
  {
    id: '4',
    severity: 'medium',
    title: 'Weak Password Policy',
    description: 'Password validation allows weak passwords',
    file: 'src/validation/auth.js',
    line: 67,
    cve: null,
    remediation: 'Implement stronger password requirements including minimum length, character diversity, and common password checking.',
    example: `// Current validation:
password.length >= 6

// Improved validation:
const strongPassword = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{12,}$/;
strongPassword.test(password);`
  },
  {
    id: '5',
    severity: 'low',
    title: 'Information Disclosure',
    description: 'Detailed error messages expose sensitive information',
    file: 'src/middleware/errorHandler.js',
    line: 15,
    cve: null,
    remediation: 'Log detailed errors internally but return generic error messages to users.',
    example: `// Vulnerable code:
res.status(500).json({ error: error.message, stack: error.stack });

// Fixed code:
logger.error(error); // Log internally
res.status(500).json({ error: 'Internal server error' });`
  },
  {
    id: '6',
    severity: 'low',
    title: 'Missing Security Headers',
    description: 'HTTP security headers not configured',
    file: 'src/server.js',
    line: 8,
    cve: null,
    remediation: 'Add security headers like CSP, HSTS, X-Frame-Options to protect against various attacks.',
    example: `// Add security headers:
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"]
    }
  }
}));`
  }
];

const RepositoryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [repository, setRepository] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedVulnerability, setSelectedVulnerability] = useState(null);

  useEffect(() => {
    const loadRepositoryData = async () => {
      setLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock repository data
      setRepository({
        id,
        name: 'web-app',
        url: 'https://github.com/user/web-app',
        status: 'completed',
        lastScan: '2024-01-15T10:30:00Z',
        vulnerabilities: {
          high: 2,
          medium: 2,
          low: 2
        },
        totalVulnerabilities: 6
      });
      
      setVulnerabilities(mockVulnerabilities);
      setLoading(false);
    };

    loadRepositoryData();
  }, [id]);

  const handleBack = () => {
    navigate('/dashboard');
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'medium':
        return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'low':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-4 h-4" />;
      case 'medium':
        return <Clock className="w-4 h-4" />;
      case 'low':
        return <Shield className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  const filteredVulnerabilities = selectedSeverity === 'all' 
    ? vulnerabilities 
    : vulnerabilities.filter(v => v.severity === selectedSeverity);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-3">
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
                <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/3 mb-4"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-2/3 mb-4"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <div className="flex items-center mb-8">
        <button
          onClick={handleBack}
          className="flex items-center text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3">
          {/* Repository Header */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6 transition-colors duration-300">
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <div className="bg-blue-600 dark:bg-blue-500 p-3 rounded-xl">
                  <GitBranch className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{repository?.name}</h1>
                  <a
                    href={repository?.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm flex items-center mt-1 transition-colors duration-200"
                  >
                    {repository?.url}
                    <ExternalLink className="w-4 h-4 ml-1" />
                  </a>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500 dark:text-gray-400">Last scanned</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {formatDate(repository?.lastScan)}
                </div>
              </div>
            </div>
          </div>

          {/* Vulnerability Filters */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6 transition-colors duration-300">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Vulnerability Report</h2>
            
            <div className="flex flex-wrap gap-3 mb-6">
              <button
                onClick={() => setSelectedSeverity('all')}
                className={`px-4 py-2 rounded-lg border font-medium transition-all duration-200 ${
                  selectedSeverity === 'all'
                    ? 'bg-blue-600 dark:bg-blue-500 text-white border-blue-600 dark:border-blue-500'
                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                All ({vulnerabilities.length})
              </button>
              <button
                onClick={() => setSelectedSeverity('high')}
                className={`px-4 py-2 rounded-lg border font-medium transition-all duration-200 flex items-center ${
                  selectedSeverity === 'high'
                    ? 'bg-red-600 dark:bg-red-500 text-white border-red-600 dark:border-red-500'
                    : 'bg-white dark:bg-gray-700 text-red-600 dark:text-red-400 border-red-300 dark:border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                }`}
              >
                <AlertTriangle className="w-4 h-4 mr-2" />
                High ({repository?.vulnerabilities?.high})
              </button>
              <button
                onClick={() => setSelectedSeverity('medium')}
                className={`px-4 py-2 rounded-lg border font-medium transition-all duration-200 flex items-center ${
                  selectedSeverity === 'medium'
                    ? 'bg-orange-600 dark:bg-orange-500 text-white border-orange-600 dark:border-orange-500'
                    : 'bg-white dark:bg-gray-700 text-orange-600 dark:text-orange-400 border-orange-300 dark:border-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20'
                }`}
              >
                <Clock className="w-4 h-4 mr-2" />
                Medium ({repository?.vulnerabilities?.medium})
              </button>
              <button
                onClick={() => setSelectedSeverity('low')}
                className={`px-4 py-2 rounded-lg border font-medium transition-all duration-200 flex items-center ${
                  selectedSeverity === 'low'
                    ? 'bg-yellow-600 dark:bg-yellow-500 text-white border-yellow-600 dark:border-yellow-500'
                    : 'bg-white dark:bg-gray-700 text-yellow-600 dark:text-yellow-400 border-yellow-300 dark:border-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20'
                }`}
              >
                <Shield className="w-4 h-4 mr-2" />
                Low ({repository?.vulnerabilities?.low})
              </button>
            </div>

            {/* Vulnerability List */}
            <div className="space-y-4">
              {filteredVulnerabilities.map((vuln) => (
                <div
                  key={vuln.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow duration-200 cursor-pointer bg-white dark:bg-gray-800"
                  onClick={() => setSelectedVulnerability(vuln)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(vuln.severity)}`}
                        >
                          {getSeverityIcon(vuln.severity)}
                          <span className="ml-2 capitalize">{vuln.severity}</span>
                        </span>
                        {vuln.cve && (
                          <span className="ml-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-md font-mono">
                            {vuln.cve}
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{vuln.title}</h3>
                      <p className="text-gray-600 dark:text-gray-300 mb-3">{vuln.description}</p>
                      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <FileText className="w-4 h-4 mr-1" />
                        <span>{vuln.file}:{vuln.line}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredVulnerabilities.length === 0 && (
              <div className="text-center py-8">
                <CheckCircle className="mx-auto h-12 w-12 text-green-500 dark:text-green-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                  No {selectedSeverity !== 'all' ? selectedSeverity + ' severity' : ''} vulnerabilities found
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {selectedSeverity !== 'all'
                    ? 'Try selecting a different severity level'
                    : 'Your repository looks secure!'
                  }
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Summary Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Scan Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-300">Total Issues</span>
                <span className="font-semibold text-gray-900 dark:text-white">{repository?.totalVulnerabilities}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-red-600 dark:text-red-400">High Priority</span>
                <span className="font-semibold text-red-600 dark:text-red-400">{repository?.vulnerabilities?.high}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-orange-600 dark:text-orange-400">Medium Priority</span>
                <span className="font-semibold text-orange-600 dark:text-orange-400">{repository?.vulnerabilities?.medium}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-yellow-600 dark:text-yellow-400">Low Priority</span>
                <span className="font-semibold text-yellow-600 dark:text-yellow-400">{repository?.vulnerabilities?.low}</span>
              </div>
            </div>
          </div>

          {/* Actions Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 transition-colors duration-300">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Actions</h3>
            <div className="space-y-3">
              <button className="w-full bg-blue-600 dark:bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors duration-200 flex items-center justify-center">
                <RefreshCw className="w-4 h-4 mr-2" />
                Rescan Repository
              </button>
              <button className="w-full border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                Export Report
              </button>
              <button className="w-full border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-2 px-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                Share Report
              </button>
            </div>
          </div>

          {/* Tips Card */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">Security Tips</h3>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-2">
              <li>• Address high-priority vulnerabilities first</li>
              <li>• Regular scans help maintain security</li>
              <li>• Keep dependencies updated</li>
              <li>• Follow secure coding practices</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Vulnerability Detail Modal */}
      {selectedVulnerability && (
        <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(selectedVulnerability.severity)}`}
                  >
                    {getSeverityIcon(selectedVulnerability.severity)}
                    <span className="ml-2 capitalize">{selectedVulnerability.severity}</span>
                  </span>
                  {selectedVulnerability.cve && (
                    <span className="ml-3 px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-md font-mono">
                      {selectedVulnerability.cve}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setSelectedVulnerability(null)}
                  className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-400 text-2xl"
                >
                  ×
                </button>
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-3">{selectedVulnerability.title}</h2>
            </div>
            
            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Description</h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedVulnerability.description}</p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Location</h3>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                    <FileText className="w-4 h-4 mr-2" />
                    <span className="font-mono">{selectedVulnerability.file}:{selectedVulnerability.line}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Remediation</h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">{selectedVulnerability.remediation}</p>
                
                {selectedVulnerability.example && (
                  <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-4">
                    <pre className="text-green-400 dark:text-green-300 text-sm overflow-x-auto whitespace-pre-wrap">
                      <code>{selectedVulnerability.example}</code>
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RepositoryDetail;