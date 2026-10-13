import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
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
const TestAuthProvider = ({ children }) => {
    return (_jsx(AuthContext.Provider, { value: {
            user: mockUser,
            loading: false,
            login: vi.fn(),
            logout: vi.fn(),
            refreshUser: vi.fn(),
        }, children: children }));
};
const renderWithAuth = (component) => {
    return render(_jsx(BrowserRouter, { children: _jsx(TestAuthProvider, { children: component }) }));
};
describe('Sidebar', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('renders navigation items', () => {
        renderWithAuth(_jsx(Sidebar, {}));
        expect(screen.getByText('RAG Engine')).toBeInTheDocument();
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Documents')).toBeInTheDocument();
        expect(screen.getByText('Query')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });
    it('highlights active route', () => {
        renderWithAuth(_jsx(Sidebar, {}));
        const dashboardLink = screen.getByText('Dashboard');
        expect(dashboardLink).toHaveAttribute('href', '/dashboard');
    });
    it('navigates on link click', () => {
        renderWithAuth(_jsx(Sidebar, {}));
        const documentsLink = screen.getByText('Documents');
        fireEvent.click(documentsLink);
        expect(window.location.pathname).toBe('/documents');
    });
    it('shows user info when authenticated', () => {
        renderWithAuth(_jsx(Sidebar, {}));
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('Roles: viewer')).toBeInTheDocument();
        expect(screen.getByText('Logout')).toBeInTheDocument();
    });
});
