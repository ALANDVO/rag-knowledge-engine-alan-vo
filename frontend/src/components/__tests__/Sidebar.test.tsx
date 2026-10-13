import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ReactNode } from 'react';
import { AuthContext } from '../../App';
import Sidebar from '../Sidebar';

// Mock user for testing
const mockUser = {
  sub: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  roles: ['viewer'],
};

// Test AuthProvider that provides a mock user context
const TestAuthProvider = ({ children }: { children: ReactNode }) => {
  return (
    <AuthContext.Provider
      value={{
        user: mockUser,
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        refreshUser: vi.fn(),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

const renderWithAuth = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      <TestAuthProvider>
        {component}
      </TestAuthProvider>
    </BrowserRouter>
  );
};

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders navigation items', () => {
    renderWithAuth(<Sidebar />);
    expect(screen.getByText('RAG Engine')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Query')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('highlights active route', () => {
    renderWithAuth(<Sidebar />);
    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink).toHaveAttribute('href', '/dashboard');
  });

  it('navigates on link click', () => {
    renderWithAuth(<Sidebar />);
    const documentsLink = screen.getByText('Documents');
    fireEvent.click(documentsLink);
    expect(window.location.pathname).toBe('/documents');
  });

  it('shows user info when authenticated', () => {
    renderWithAuth(<Sidebar />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('Roles: viewer')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });
});