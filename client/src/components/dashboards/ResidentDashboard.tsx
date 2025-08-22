import React, { useState, useRef, useEffect } from 'react';
import { CpuChipIcon, PaperAirplaneIcon, LightBulbIcon, ChartBarIcon, UserIcon, SparklesIcon, ExclamationTriangleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import Plot from 'react-plotly.js';
import { apiClient } from '../../services/api';
import { tokenManager } from '../../services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  chartData?: any;
  metadata?: any;
}

interface FAQItem {
  question: string;
  description: string;
  icon: React.ComponentType<any>;
  category: string;
}

const ResidentDashboard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your Pension AI assistant. I can help you understand your pension data, analyze risk scores, detect fraud, and provide insights. What would you like to know?",
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFAQ, setSelectedFAQ] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showWelcome, setShowWelcome] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get current user on component mount
  useEffect(() => {
    const user = tokenManager.getUser();
    setCurrentUser(user);
  }, []);

  const faqItems: FAQItem[] = [
    {
      question: "What's my risk score?",
      description: "Get your personalized risk assessment with visual charts",
      icon: ChartBarIcon,
      category: "analysis"
    },
    {
      question: "How secure is my pension?",
      description: "Fraud detection and security analysis",
      icon: LightBulbIcon,
      category: "security"
    },
    {
      question: "What's my projected pension?",
      description: "Future pension amount predictions and analysis",
      icon: ChartBarIcon,
      category: "projections"
    },
    {
      question: "Portfolio analysis",
      description: "Detailed breakdown of your investment portfolio",
      icon: ChartBarIcon,
      category: "analysis"
    },
    {
      question: "Compare pension options",
      description: "Compare different pension schemes and benefits",
      icon: ChartBarIcon,
      category: "comparison"
    },
    {
      question: "Tax implications",
      description: "Understand tax benefits and implications",
      icon: LightBulbIcon,
      category: "tax"
    }
  ];

  const categories = [
    { id: 'all', name: 'All Questions', count: faqItems.length },
    { id: 'analysis', name: 'Analysis', count: faqItems.filter(item => item.category === 'analysis').length },
    { id: 'security', name: 'Security', count: faqItems.filter(item => item.category === 'security').length },
    { id: 'projections', name: 'Projections', count: faqItems.filter(item => item.category === 'projections').length },
    { id: 'comparison', name: 'Comparison', count: faqItems.filter(item => item.category === 'comparison').length },
    { id: 'tax', name: 'Tax', count: faqItems.filter(item => item.category === 'tax').length }
  ];

  const filteredFAQItems = selectedCategory === 'all' 
    ? faqItems 
    : faqItems.filter(item => item.category === selectedCategory);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowWelcome(false);

    try {
      // Call the real AI API endpoint
      console.log('Sending query to AI API:', inputValue);
      const response = await apiClient.processPrompt(inputValue);
      
      console.log('AI API Response:', response);
      
      // Debug chart data
      if (response.chart_data) {
        console.log('Chart data received:', response.chart_data);
        console.log('Chart data keys:', Object.keys(response.chart_data));
        console.log('First chart structure:', response.chart_data[Object.keys(response.chart_data)[0]]);
        console.log('Chart data type:', typeof response.chart_data);
        console.log('Chart data length:', Object.keys(response.chart_data).length);
      } else {
        console.log('No chart_data in response');
        console.log('Available response keys:', Object.keys(response));
        console.log('Full response:', response);
      }
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.summary || 'No response received from AI',
        timestamp: new Date(),
        chartData: response.chart_data || null,
        metadata: response.metadata || null,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('AI API Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I apologize, but I encountered an error: ${error.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFAQClick = (question: string) => {
    setSelectedFAQ(question);
    setInputValue(question);
    setShowWelcome(false);
  };

  const handleLogout = () => {
    tokenManager.logout();
    // Redirect to landing page or refresh the page
    window.location.href = '/';
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      analysis: 'bg-blue-100 text-blue-800 border-blue-200',
      security: 'bg-green-100 text-green-800 border-green-200',
      projections: 'bg-purple-100 text-purple-800 border-purple-200',
      comparison: 'bg-orange-100 text-orange-800 border-orange-200',
      tax: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Single Consolidated Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
              <CpuChipIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Pension AI</h1>
              <p className="text-sm text-gray-500">Your Personal Pension Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {/* Status Indicator */}
            <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 rounded-full border border-green-200">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-700 font-medium">Connected</span>
            </div>
            
            {/* User Info */}
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <UserIcon className="h-5 w-5" />
              <span>Member Dashboard</span>
            </div>

            {/* User Details and Logout */}
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  Welcome, {currentUser?.full_name || currentUser?.username || 'User'}
                </p>
                <p className="text-xs text-gray-500">
                  ID: {currentUser?.id || 'N/A'}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors duration-200"
              >
                <ArrowRightOnRectangleIcon className="h-4 w-4" />
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col">
          {/* Welcome Banner */}
          {showWelcome && (
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 px-6 py-4 text-white">
              <div className="flex items-center space-x-3">
                <SparklesIcon className="h-6 w-6" />
                <div>
                  <h3 className="font-semibold">Welcome to Pension AI!</h3>
                  <p className="text-sm text-blue-100">Ask me anything about your pension - I'm here to help you understand your financial future.</p>
                </div>
                <button 
                  onClick={() => setShowWelcome(false)}
                  className="ml-auto text-blue-100 hover:text-white transition-colors"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                      : 'bg-white text-gray-900 shadow-md border border-gray-100'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    {message.type === 'assistant' && (
                      <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                        <CpuChipIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                       
                      {/* Enhanced Chart Display */}

                      {(() => {
                        console.log('Rendering charts with data:', message.chartData);
                        return null;
                      })()}
                      {message.chartData && Object.keys(message.chartData).length > 0 && (
                        <div className="mt-4 space-y-4">
                          {Object.entries(message.chartData).map(([chartKey, chartConfig]: [string, any]) => {
                            console.log(`Rendering chart ${chartKey}:`, chartConfig);
                            return (
    
                            <div key={chartKey} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                              <div className="flex items-center space-x-2 mb-3">
                                <ChartBarIcon className="h-5 w-5 text-blue-500" />
                                <h4 className="font-medium text-gray-900 capitalize">
                                  {chartKey.replace(/([A-Z])/g, ' $1').trim()}
                                </h4>
                              </div>
                              <div className="bg-white rounded border p-2">
                                <Plot
                                  data={[
                                    {
                                      // Handle different chart types based on mark type
                                      x: chartConfig.mark === 'bar' 
                                        ? chartConfig.data.values.map((v: any) => v.category || v.metric || Object.values(v)[0])
                                        : chartConfig.data.values.map((v: any) => v.age || v[Object.keys(v)[0]]),
                                      y: chartConfig.mark === 'bar'
                                        ? chartConfig.data.values.map((v: any) => v.amount || v.value || v[Object.keys(v)[1]])
                                        : chartConfig.data.values.map((v: any) => v.projected_value || v[Object.keys(v)[1]]),
                                      type: chartConfig.mark === 'bar' ? 'bar' : 'scatter',
                                      mode: chartConfig.mark === 'line' ? 'lines' : undefined,
                                      marker: {
                                        color: chartConfig.mark === 'bar' ? ['#3B82F6', '#10B981', '#F59E0B'] : '#3B82F6',
                                        size: 8
                                      },
                                      line: {
                                        color: '#3B82F6',
                                        width: 3
                                      }
                                    }
                                  ]}
                                  layout={{
                                    width: 400,
                                    height: 300,
                                    margin: { l: 50, r: 20, t: 20, b: 50 },
                                    xaxis: { 
                                      title: chartConfig.encoding?.x?.title || '',
                                      gridcolor: '#e0e0e0'
                                    },
                                    yaxis: { 
                                      title: chartConfig.encoding?.y?.title || '',
                                      gridcolor: '#e0e0e0'
                                    },
                                    showlegend: false,
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                  }}
                                  config={{ displayModeBar: false }}
                                />
                              </div>
                            </div>
                            );
                          })}
                        </div>
                      )}
                       
                      <div className="text-xs text-gray-400 mt-2">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Enhanced Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl px-4 py-3 shadow-md border border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-md">
                      <CpuChipIcon className="h-4 w-4 text-white" />
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">AI is thinking</span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Enhanced Input Area */}
          <div className="border-t border-gray-200 bg-white px-6 py-4 shadow-sm">
            <div className="flex space-x-4">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask me anything about your pension..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 pr-12"
                  disabled={isLoading}
                />
                {inputValue && (
                  <button
                    onClick={() => setInputValue('')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    ×
                  </button>
                )}
              </div>
              <button
                className="px-4 py-3 bg-gray-100 text-gray-600 rounded-xl hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 flex items-center space-x-2"
                title="Upload PDF"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <span className="hidden sm:inline">PDF</span>
              </button>
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl hover:from-blue-600 hover:to-purple-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 shadow-lg"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced FAQ Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 shadow-lg overflow-y-auto">
          <div className="p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Questions</h3>
              <p className="text-sm text-gray-600 mb-4">Click on any question to get started</p>
              
              {/* Category Filter */}
              <div className="flex flex-wrap gap-2 mb-4">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
                      selectedCategory === category.id
                        ? 'bg-blue-500 text-white shadow-md'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {category.name} ({category.count})
                  </button>
                ))}
              </div>
            </div>
            
            <div className="space-y-3">
              {filteredFAQItems.map((item, index) => (
                <button
                  key={index}
                  onClick={() => handleFAQClick(item.question)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                    selectedFAQ === item.question
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200 shadow-md'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 hover:shadow-sm'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${
                      selectedFAQ === item.question ? 'bg-blue-500' : 'bg-gray-100'
                    }`}>
                      <item.icon className={`h-4 w-4 ${
                        selectedFAQ === item.question ? 'text-white' : 'text-gray-600'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className={`font-medium text-sm ${
                          selectedFAQ === item.question ? 'text-blue-900' : 'text-gray-900'
                        }`}>
                          {item.question}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs border ${getCategoryColor(item.category)}`}>
                          {item.category}
                        </span>
                      </div>
                      <p className={`text-xs ${
                        selectedFAQ === item.question ? 'text-blue-700' : 'text-gray-500'
                      }`}>
                        {item.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Quick Tips */}
            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-start space-x-3">
                <ExclamationTriangleIcon className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="text-sm font-medium text-blue-900">Pro Tips</h4>
                  <ul className="text-xs text-blue-700 mt-1 space-y-1">
                    <li>• Be specific with your questions for better answers</li>
                    <li>• Ask about risk scores, projections, or security</li>
                    <li>• Upload PDFs for document analysis</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResidentDashboard;
