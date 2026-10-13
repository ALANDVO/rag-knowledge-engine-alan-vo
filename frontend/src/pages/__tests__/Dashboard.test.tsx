import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../Dashboard';

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockReset();
  });

  it('renders dashboard title', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ total_vectors: 0, status: 'ok' }),
    });
    renderWithRouter(<Dashboard />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    let resolveFetch: any;
    (global.fetch as any).mockImplementation(() => new Promise(r => { resolveFetch = r; }));
    renderWithRouter(<Dashboard />);
    expect(screen.getByText('...')).toBeInTheDocument();
  });

  it('displays vector count after fetch', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ total_vectors: 42, status: 'ok' }),
    });
    renderWithRouter(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText('42')).toBeInTheDocument();
    });
  });

  it('shows online status', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ total_vectors: 0, status: 'ok' }),
    });
    renderWithRouter(<Dashboard />);
    expect(screen.getByText('Online')).toBeInTheDocument();
  });

  it('shows version', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ total_vectors: 0, status: 'ok' }),
    });
    renderWithRouter(<Dashboard />);
    expect(screen.getByText('1.0.0')).toBeInTheDocument();
  });

  it('handles fetch error gracefully', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));
    renderWithRouter(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText('...')).toBeInTheDocument();
    });
  });
});