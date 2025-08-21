import React, { useState, useRef, useEffect } from 'react';
import { CpuChipIcon, PaperAirplaneIcon, LightBulbIcon, ChartBarIcon, UserIcon } from '@heroicons/react/24/outline';
import Plot from 'react-plotly.js';
import { apiClient } from '../../services/api';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const faqItems: FAQItem[] = [
    {
      question: "What's my risk score?",
      description: "Get your personalized risk assessment with visual charts",
      icon: ChartBarIcon
    },
    {
      question: "How secure is my pension?",
      description: "Fraud detection and security analysis",
      icon: LightBulbIcon
    },
    {
      question: "What's my projected pension?",
      description: "Future pension amount predictions and analysis",
      icon: ChartBarIcon
    },
    {
      question: "Portfolio analysis",
      description: "Detailed breakdown of your investment portfolio",
      icon: ChartBarIcon
    }
  ];

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

    try {
      // Call the real AI API endpoint
      console.log('Sending query to AI API:', inputValue);
      const response = await apiClient.processPrompt(inputValue);
      
      console.log('AI API Response:', response);
      
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
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <CpuChipIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Pension AI</h1>
              <p className="text-sm text-gray-500">Your Personal Pension Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <UserIcon className="h-5 w-5" />
            <span>Member Dashboard</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-900 shadow-sm border border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    {message.type === 'assistant' && (
                      <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <CpuChipIcon className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      
                      {/* Chart Display */}
                      {message.chartData && Object.keys(message.chartData).length > 0 && (
                        <div className="mt-4 space-y-4">
                          {Object.entries(message.chartData).map(([chartKey, chartConfig]: [string, any]) => (
                            <div key={chartKey} className="bg-gray-50 rounded-lg p-4">
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
                                      x: chartConfig.data.values.map((v: any) => v[Object.keys(v)[0]]),
                                      y: chartConfig.data.values.map((v: any) => v[Object.keys(v)[1]]),
                                      type: chartConfig.mark === 'bar' ? 'bar' : 'scatter',
                                      mode: chartConfig.mark === 'line' ? 'lines+markers' : undefined,
                                      marker: {
                                        color: '#3B82F6',
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
                                    xaxis: { title: chartConfig.encoding?.x?.title || '' },
                                    yaxis: { title: chartConfig.encoding?.y?.title || '' },
                                    showlegend: false,
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                  }}
                                  config={{ displayModeBar: false }}
                                />
                              </div>
                            </div>
                          ))}
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
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                      <CpuChipIcon className="h-4 w-4 text-white" />
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 bg-white px-6 py-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask me anything about your pension..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  disabled={isLoading}
                />
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
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl hover:from-blue-600 hover:to-purple-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
              >
                <PaperAirplaneIcon className="h-5 w-5" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>

        {/* FAQ Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 p-6 overflow-y-auto">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Questions</h3>
            <p className="text-sm text-gray-600">Click on any question to get started</p>
          </div>
          
          <div className="space-y-3">
            {faqItems.map((item, index) => (
              <button
                key={index}
                onClick={() => handleFAQClick(item.question)}
                className={`w-full text-left p-4 rounded-lg border transition-all duration-200 ${
                  selectedFAQ === item.question
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-full ${
                    selectedFAQ === item.question ? 'bg-blue-500' : 'bg-gray-100'
                  }`}>
                    <item.icon className={`h-4 w-4 ${
                      selectedFAQ === item.question ? 'text-white' : 'text-gray-600'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className={`font-medium text-sm ${
                      selectedFAQ === item.question ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                      {item.question}
                    </h4>
                    <p className={`text-xs mt-1 ${
                      selectedFAQ === item.question ? 'text-blue-700' : 'text-gray-500'
                    }`}>
                      {item.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* API Connection Info */}
          <div className="mt-8 p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-start space-x-3">
              <LightBulbIcon className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-green-900">Connected to AI API</h4>
                <p className="text-xs text-green-700 mt-1">
                  This dashboard is now connected to your Pension AI backend. Ask questions about your pension data and get real-time AI-powered insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResidentDashboard;
