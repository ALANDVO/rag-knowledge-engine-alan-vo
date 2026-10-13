import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';
const renderWithRouter = (component) => {
    return render(_jsx(BrowserRouter, { children: component }));
};
describe('Dashboard', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch.mockReset();
    });
    it('renders dashboard title', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ total_vectors: 0, status: 'ok' }),
        });
        renderWithRouter(_jsx(Dashboard, {}));
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
    it('shows loading state initially', () => {
        let resolveFetch;
        global.fetch.mockImplementation(() => new Promise(r => { resolveFetch = r; }));
        renderWithRouter(_jsx(Dashboard, {}));
        expect(screen.getByText('...')).toBeInTheDocument();
    });
    it('displays vector count after fetch', async () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ total_vectors: 42, status: 'ok' }),
        });
        renderWithRouter(_jsx(Dashboard, {}));
        await waitFor(() => {
            expect(screen.getByText('42')).toBeInTheDocument();
        });
    });
    it('shows online status', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ total_vectors: 0, status: 'ok' }),
        });
        renderWithRouter(_jsx(Dashboard, {}));
        expect(screen.getByText('Online')).toBeInTheDocument();
    });
    it('shows version', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ total_vectors: 0, status: 'ok' }),
        });
        renderWithRouter(_jsx(Dashboard, {}));
        expect(screen.getByText('1.0.0')).toBeInTheDocument();
    });
    it('handles fetch error gracefully', async () => {
        global.fetch.mockRejectedValue(new Error('Network error'));
        renderWithRouter(_jsx(Dashboard, {}));
        await waitFor(() => {
            expect(screen.getByText('...')).toBeInTheDocument();
        });
    });
});
