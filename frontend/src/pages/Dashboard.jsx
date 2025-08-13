import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, GitBranch, AlertTriangle, CheckCircle, Clock, Eye, RefreshCw, Search } from 'lucide-react';

// Mock data for demonstration
const mockRepositories = [
  {
    id: '1',
    name: 'web-app',
    url: 'https://github.com/user/web-app',
    status: 'completed',
    lastScan: '2024-01-15T10:30:00Z',
    vulnerabilities: {
      high: 3,
      medium: 7,
      low: 12
    },
    totalVulnerabilities: 22
  },
  {
    id: '2',
    name: 'api-service',
    url: 'https://github.com/user/api-service',
    status: 'scanning',
    lastScan: '2024-01-15T11:45:00Z',
    vulnerabilities: null,
    totalVulnerabilities: 0
  },
  {
    id: '3',
    name: 'mobile-client',
    url: 'https://github.com/user/mobile-client',
    status: 'completed',
    lastScan: '2024-01-14T15:20:00Z',
    vulnerabilities: {
      high: 1,
      medium: 3,
      low: 8
    },
    totalVulnerabilities: 12
  },
  {
    id: '4',
    name: 'data-pipeline',
    url: 'https://github.com/user/data-pipeline',
    status: 'error',
    lastScan: '2024-01-14T09:15:00Z',
    vulnerabilities: null,
    totalVulnerabilities: 0
  }
];

const Dashboard = () => {
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Simulate API call
    const loadRepositories = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setRepositories(mockRepositories);
      setLoading(false);
    };

    loadRepositories();
  }, []);

  const filteredRepositories = repositories.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.url.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleRescan = (repoId) => {
    setRepositories(repos =>
      repos.map(repo =>
        repo.id === repoId ? { ...repo, status: 'scanning' } : repo
      )
    );

    // Simulate rescan completion
    setTimeout(() => {
      setRepositories(repos =>
        repos.map(repo =>
          repo.id === repoId
            ? {
                ...repo,
                status: 'completed',
                lastScan: new Date().toISOString(),
                vulnerabilities: {
                  high: Math.floor(Math.random() * 5),
                  medium: Math.floor(Math.random() * 10),
                  low: Math.floor(Math.random() * 15)
                }
              }
            : repo
        )
      );
    }, 3000);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-4 h-4 mr-1" />
            Completed
          </span>
        );
      case 'scanning':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-800 mr-1"></div>
            Scanning
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <AlertTriangle className="w-4 h-4 mr-1" />
            Error
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
            <Clock className="w-4 h-4 mr-1" />
            Pending
          </span>
        );
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-orange-600 bg-orange-100';
      case 'low':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-4"></div>
                <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
              </div>
            ))}
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6">
              <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded w-1/3 mb-4"></div>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-16 bg-gray-300 dark:bg-gray-600 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalVulnerabilities = repositories.reduce((acc, repo) => acc + repo.totalVulnerabilities, 0);
  const completedScans = repositories.filter(repo => repo.status === 'completed').length;
  const activeScans = repositories.filter(repo => repo.status === 'scanning').length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Security Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">Monitor and manage your repository vulnerabilities</p>
        </div>
        <Link
          to="/add-repository"
          className="mt-4 sm:mt-0 inline-flex items-center px-6 py-3 bg-blue-600 dark:bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 focus:ring-4 focus:ring-blue-200 dark:focus:ring-blue-800 transition-all duration-200 shadow-sm"
        >
          <Plus className="w-5 h-5 mr-2" />
          Add Repository
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-700 transition-colors duration-300">
          <div className="flex items-center">
            <div className="p-3 bg-blue-900/30 rounded-lg">
              <GitBranch className="w-6 h-6 text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-400">Total Repositories</p>
              <p className="text-2xl font-bold text-white">{repositories.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors duration-300">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Vulnerabilities</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalVulnerabilities}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors duration-300">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed Scans</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{completedScans}</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors duration-300">
          <div className="flex items-center">
            <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Scans</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeScans}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Repository List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors duration-300">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Repositories</h2>
            <div className="mt-4 sm:mt-0 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400 dark:text-gray-500" />
              </div>
              <input
                type="text"
                placeholder="Search repositories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Repository
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Vulnerabilities
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Last Scan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredRepositories.map((repo) => (
                <tr key={repo.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{repo.name}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{repo.url}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(repo.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {repo.vulnerabilities ? (
                      <div className="flex space-x-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getSeverityColor('high')}`}>
                          High: {repo.vulnerabilities.high}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getSeverityColor('medium')}`}>
                          Med: {repo.vulnerabilities.medium}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getSeverityColor('low')}`}>
                          Low: {repo.vulnerabilities.low}
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500 dark:text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {formatDate(repo.lastScan)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    {repo.status === 'completed' && (
                      <Link
                        to={`/repository/${repo.id}`}
                        className="inline-flex items-center px-3 py-2 border border-gray-600 rounded-md text-sm font-medium text-gray-300 bg-gray-700 hover:bg-gray-600 transition-colors duration-200"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Link>
                    )}
                    <button
                      onClick={() => handleRescan(repo.id)}
                      disabled={repo.status === 'scanning'}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <RefreshCw className={`w-4 h-4 mr-1 ${repo.status === 'scanning' ? 'animate-spin' : ''}`} />
                      {repo.status === 'scanning' ? 'Scanning...' : 'Rescan'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredRepositories.length === 0 && (
          <div className="text-center py-12">
            <GitBranch className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No repositories found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {searchTerm ? 'Try adjusting your search terms' : 'Get started by adding a new repository'}
            </p>
            {!searchTerm && (
              <div className="mt-6">
                <Link
                  to="/add-repository"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Repository
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;