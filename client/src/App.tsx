import { useState, useEffect } from 'react';
import { CpuChipIcon } from '@heroicons/react/24/outline';
import PensionAILanding from './pages/LandingPage';
import Login from './components/auth/Login';
import Signup from './components/auth/Signup';
import ResidentDashboard from './components/dashboards/ResidentDashboard';
import AdvisorDashboard from './components/dashboards/AdvisorDashboard';
import RegulatorDashboard from './components/dashboards/RegulatorDashboard';
import { tokenManager } from './services/api';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);

  const pages = [
    { id: 'landing', name: 'Landing Page', component: PensionAILanding },
    { id: 'login', name: 'Login', component: Login },
    { id: 'signup', name: 'Signup', component: Signup },
    { id: 'resident', name: 'Resident Dashboard', component: ResidentDashboard },
    { id: 'advisor', name: 'Advisor Dashboard', component: AdvisorDashboard },
    { id: 'regulator', name: 'Regulator Dashboard', component: RegulatorDashboard },
  ];

  // Check authentication status on component mount
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = tokenManager.isAuthenticated();
      const user = tokenManager.getUser();
      setIsAuthenticated(authenticated);
      setCurrentUser(user);
      
      // If authenticated, redirect to appropriate dashboard
      if (authenticated && user) {
        setCurrentPage(user.role === 'resident' ? 'resident' : 
                     user.role === 'advisor' ? 'advisor' : 
                     user.role === 'regulator' ? 'regulator' : 'resident');
      }
    };

    checkAuth();
  }, []);

  // Handle successful login
  const handleLoginSuccess = (userData: any) => {
    setIsAuthenticated(true);
    setCurrentUser(userData);
    
    // Redirect to appropriate dashboard based on role
    const targetPage = userData.role === 'resident' ? 'resident' : 
                      userData.role === 'advisor' ? 'advisor' : 
                      userData.role === 'regulator' ? 'regulator' : 'resident';
    setCurrentPage(targetPage);
  };

  // Handle logout
  const handleLogout = () => {
    tokenManager.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCurrentPage('landing');
  };

  const CurrentComponent = pages.find(page => page.id === currentPage)?.component || PensionAILanding;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <CpuChipIcon className="h-5 w-5 text-white" />
                </div>
                <span className="ml-2 text-xl font-bold text-gray-900">Pension AI</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {!isAuthenticated ? (
                // Show login/signup for unauthenticated users
                <>
                  <button
                    onClick={() => setCurrentPage('login')}
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                  >
                    Login
                  </button>
                  <button
                    onClick={() => setCurrentPage('signup')}
                    className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                  >
                    Sign Up
                  </button>
                </>
              ) : (
                // Show user info and logout for authenticated users
                <>
                  <span className="text-sm text-gray-700">
                    Welcome, {currentUser?.full_name} ({currentUser?.role})
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors duration-200"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {currentPage === 'login' ? (
          <Login onLoginSuccess={handleLoginSuccess} />
        ) : currentPage === 'signup' ? (
          <Signup />
        ) : (
          <CurrentComponent />
        )}
      </main>
    </div>
  );
}

export default App;