import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { apiClient } from '../../services/api';
import { 
  Shield, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  BarChart3, 
  PieChart, 
  Filter,
  RefreshCw,
  Send,
  Eye,
  TrendingDown,
  Activity
} from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  chartData?: any;
}

interface RegulatorData {
  regulator_id: number;
  total_users: number;
  grouped_data: {
    by_risk_tolerance: Record<string, { count: number; users: RegulatorUser[] }>;
    by_age_group: Record<string, { count: number; users: RegulatorUser[] }>;
    by_income_level: Record<string, { count: number; users: RegulatorUser[] }>;
  };
  summary: {
    total_users: number;
    avg_age: number;
    avg_income: number;
    avg_savings: number;
    risk_distribution: Record<string, number>;
    fraud_risk_summary: { high: number; medium: number; low: number };
  };
}

interface RegulatorUser {
  user_id: number;
  full_name: string;
  age: number;
  annual_income: number;
  current_savings: number;
  risk_tolerance: string;
  anomaly_score: number;
  role: string;
}

const RegulatorDashboard: React.FC = () => {
  const [regulatorData, setRegulatorData] = useState<RegulatorData | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Simple filters
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('all');
  const [selectedAgeGroup, setSelectedAgeGroup] = useState<string>('all');
  const [selectedIncomeLevel, setSelectedIncomeLevel] = useState<string>('all');

  const quickQueries = [
    "Show high-risk members",
    "Fraud detection summary",
    "Geographic risk analysis",
    "Portfolio performance trends",
    "Suspicious activity report",
    "Compliance overview"
  ];

  // Load regulator dashboard data on component mount
  useEffect(() => {
    loadRegulatorDashboard();
  }, []);

  // Initialize welcome message
  useEffect(() => {
    if (regulatorData) {
      setMessages([
        {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Welcome to the Regulatory Oversight Dashboard! I can help you analyze ${regulatorData.total_users} members across the pension system. What would you like to investigate?`,
          timestamp: new Date()
        }
      ]);
    }
  }, [regulatorData]);

  const loadRegulatorDashboard = async () => {
    try {
      setLoadingDashboard(true);
      setError(null);
      const data = await apiClient.getRegulatorDashboard();
      setRegulatorData(data);
    } catch (err) {
      setError('Failed to load regulatory dashboard data. Please try again.');
      console.error('Error loading regulator dashboard:', err);
    } finally {
      setLoadingDashboard(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await apiClient.processPrompt(inputValue);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.summary,
        timestamp: new Date(),
        chartData: response.chart_data,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickQuery = (query: string) => {
    setInputValue(query);
  };

  if (loadingDashboard) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800">Loading Regulatory Dashboard</h2>
          <p className="text-gray-600">Please wait...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadRegulatorDashboard}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="h-5 w-5 inline mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!regulatorData) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">No Regulatory Data Available</h2>
          <p className="text-gray-600">Unable to load regulatory oversight data.</p>
        </div>
      </div>
    );
  }

  // Prepare data for interactive charts
  const riskData = Object.entries(regulatorData.summary.risk_distribution).map(([risk, count]) => ({
    risk,
    count,
    color: risk.toLowerCase().includes('high') ? '#ef4444' : 
           risk.toLowerCase().includes('medium') ? '#f59e0b' : '#10b981'
  }));

  const ageGroups = Object.entries(regulatorData.grouped_data.by_age_group).map(([age, data]) => ({
    age,
    count: data.count,
    avgIncome: data.users.reduce((sum, user) => sum + (user.annual_income || 0), 0) / data.count,
    avgSavings: data.users.reduce((sum, user) => sum + (user.current_savings || 0), 0) / data.count
  }));

  const incomeGroups = Object.entries(regulatorData.grouped_data.by_income_level).map(([income, data]) => ({
    income,
    count: data.count,
    avgAge: data.users.reduce((sum, user) => sum + (user.age || 0), 0) / data.count,
    avgSavings: data.users.reduce((sum, user) => sum + (user.current_savings || 0), 0) / data.count
  }));

  const fraudRiskData = [
    { risk: 'High Risk', count: regulatorData.summary.fraud_risk_summary.high, color: '#ef4444' },
    { risk: 'Medium Risk', count: regulatorData.summary.fraud_risk_summary.medium, color: '#f59e0b' },
    { risk: 'Low Risk', count: regulatorData.summary.fraud_risk_summary.low, color: '#10b981' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Regulatory Oversight Dashboard</h1>
                <p className="text-gray-600">Comprehensive pension system monitoring and fraud detection</p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <p className="text-sm text-gray-500">Total Members</p>
                <p className="text-2xl font-bold text-blue-600">{regulatorData.total_users.toLocaleString()}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">High Risk</p>
                <p className="text-2xl font-bold text-red-600">{regulatorData.summary.fraud_risk_summary.high}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-500">Avg Portfolio</p>
                <p className="text-xl font-bold text-green-600">£{(regulatorData.summary.avg_savings / 1000).toFixed(0)}k</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select
            value={selectedRiskLevel}
            onChange={(e) => setSelectedRiskLevel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>

          <select
            value={selectedAgeGroup}
            onChange={(e) => setSelectedAgeGroup(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Age Groups</option>
            <option value="18-30">18-30</option>
            <option value="31-45">31-45</option>
            <option value="46-60">46-60</option>
            <option value="60+">60+</option>
          </select>

          <select
            value={selectedIncomeLevel}
            onChange={(e) => setSelectedIncomeLevel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Income Levels</option>
            <option value="low">Low (&lt;£30k)</option>
            <option value="medium">Medium (£30k-£70k)</option>
            <option value="high">High (&gt;£70k)</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Average Age</p>
                <p className="text-2xl font-bold text-gray-900">{regulatorData.summary.avg_age}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Average Income</p>
                <p className="text-2xl font-bold text-gray-900">£{(regulatorData.summary.avg_income / 1000).toFixed(0)}k</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div className="text-right">
                <p className="text-sm text-red-600">Suspicious Transactions</p>
                <p className="text-2xl font-bold text-red-600">{regulatorData.summary.fraud_risk_summary.medium + regulatorData.summary.fraud_risk_summary.high}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Average Savings</p>
                <p className="text-2xl font-bold text-gray-900">£{(regulatorData.summary.avg_savings / 1000).toFixed(0)}k</p>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Interactive Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Risk Distribution Chart */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <BarChart3 className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Risk Distribution Analysis</h3>
            </div>
            <div className="h-80">
              <Plot
                data={[
                  {
                    x: riskData.map(d => d.risk),
                    y: riskData.map(d => d.count),
                    type: 'bar',
                    marker: {
                      color: riskData.map(d => d.color),
                      line: { width: 2, color: 'white' }
                    },
                    hovertemplate: '<b>%{x}</b><br>Members: %{y}<extra></extra>',
                    hoverlabel: { bgcolor: 'white', font: { color: 'black' } }
                  }
                ]}
                layout={{
                  title: 'Risk Distribution Analysis',
                  xaxis: { title: 'Risk Level', showgrid: false },
                  yaxis: { title: 'Number of Members', showgrid: true, gridcolor: '#e5e7eb' },
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  margin: { t: 40, b: 60, l: 60, r: 40 },
                  showlegend: false,
                  hovermode: 'closest'
                }}
                config={{ displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d'] }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          {/* Fraud Risk Summary Chart */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <PieChart className="h-6 w-6 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Fraud Risk Summary</h3>
            </div>
            <div className="h-80">
              <Plot
                data={[
                  {
                    labels: fraudRiskData.map(d => d.risk),
                    values: fraudRiskData.map(d => d.count),
                    type: 'pie',
                    marker: {
                      colors: fraudRiskData.map(d => d.color),
                      line: { width: 2, color: 'white' }
                    },
                    hovertemplate: '<b>%{label}</b><br>Members: %{value}<br>Percentage: %{percent}<extra></extra>',
                    hoverlabel: { bgcolor: 'white', font: { color: 'black' } },
                    textinfo: 'label+percent',
                    textposition: 'outside'
                  }
                ]}
                layout={{
                  title: 'Fraud Risk Summary',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  margin: { t: 40, b: 40, l: 40, r: 40 },
                  showlegend: false,
                  hovermode: 'closest'
                }}
                config={{ displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d'] }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>
        </div>

        {/* Additional Interactive Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Age Group Analysis */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <Users className="h-6 w-6 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Age Group Analysis</h3>
            </div>
            <div className="h-80">
              <Plot
                data={[
                  {
                    x: ageGroups.map(d => d.age),
                    y: ageGroups.map(d => d.avgIncome / 1000),
                    type: 'bar',
                    name: 'Avg Income (£k)',
                    marker: { color: '#3b82f6' },
                    yaxis: 'y'
                  },
                  {
                    x: ageGroups.map(d => d.age),
                    y: ageGroups.map(d => d.avgSavings / 1000),
                    type: 'bar',
                    name: 'Avg Savings (£k)',
                    marker: { color: '#10b981' },
                    yaxis: 'y2'
                  }
                ]}
                layout={{
                  title: 'Age Group Analysis',
                  xaxis: { title: 'Age Group' },
                  yaxis: { title: 'Average Income (£k)', side: 'left' },
                  yaxis2: { title: 'Average Savings (£k)', side: 'right', overlaying: 'y' },
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  margin: { t: 40, b: 60, l: 60, r: 60 },
                  hovermode: 'closest'
                }}
                config={{ displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d'] }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          {/* Income Level Analysis */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center space-x-3 mb-4">
              <TrendingUp className="h-6 w-6 text-orange-600" />
              <h3 className="text-lg font-semibold text-gray-900">Income Level Analysis</h3>
            </div>
            <div className="h-80">
              <Plot
                data={[
                  {
                    x: incomeGroups.map(d => d.income),
                    y: incomeGroups.map(d => d.avgAge),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Average Age',
                    marker: { size: 10, color: '#f59e0b' },
                    line: { width: 3 }
                  },
                  {
                    x: incomeGroups.map(d => d.income),
                    y: incomeGroups.map(d => d.avgSavings / 1000),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Average Savings (£k)',
                    marker: { size: 10, color: '#8b5cf6' },
                    line: { width: 3 },
                    yaxis: 'y2'
                  }
                ]}
                layout={{
                  title: { text: 'Income Level Analysis' },
                  xaxis: { title: 'Income Level' },
                  yaxis: { title: 'Average Age' },
                  yaxis2: { title: 'Average Savings (£k)', side: 'right', overlaying: 'y' },
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  margin: { t: 40, b: 60, l: 60, r: 60 },
                  hovermode: 'closest'
                }}
                config={{ displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'lasso2d'] }}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* AI Assistant Chat Box - Now Horizontal Below Dashboard */}
      <div className="px-6 pb-6">
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">AI Regulatory Assistant</h3>
              <p className="text-gray-600">Ask questions about system health and compliance</p>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
            {quickQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => handleQuickQuery(query)}
                className="p-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors hover:shadow-md"
              >
                {query}
              </button>
            ))}
          </div>

          {/* Chat Interface */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat Input */}
            <div className="lg:col-span-2">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about compliance, risks, or trends..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Processing...' : (
                    <>
                      <Send className="h-4 w-4 inline mr-2" />
                      Send
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="lg:col-span-1">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Quick Stats</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Members:</span>
                    <span className="font-medium">{regulatorData.total_users}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">High Risk:</span>
                    <span className="font-medium text-red-600">{regulatorData.summary.fraud_risk_summary.high}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Age:</span>
                    <span className="font-medium">{regulatorData.summary.avg_age}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Income:</span>
                    <span className="font-medium">£{(regulatorData.summary.avg_income / 1000).toFixed(0)}k</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Display */}
          {messages.length > 1 && (
            <div className="mt-6 max-h-64 overflow-y-auto space-y-3">
              {messages.slice(1).map((message) => (
                <div
                  key={message.id}
                  className={`p-3 rounded-lg text-sm ${
                    message.type === 'user'
                      ? 'bg-blue-100 text-blue-800 ml-8'
                      : 'bg-gray-100 text-gray-800 mr-8'
                  }`}
                >
                  <p className="font-medium text-xs mb-1">
                    {message.type === 'user' ? 'You' : 'AI Assistant'}
                  </p>
                  <p>{message.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegulatorDashboard;





