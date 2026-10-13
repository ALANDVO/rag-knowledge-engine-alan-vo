import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Query from '../Query';

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Query', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockReset();
  });

  it('renders page title', () => {
    renderWithRouter(<Query />);
    expect(screen.getByText('Query')).toBeInTheDocument();
  });

  it('shows question input', () => {
    renderWithRouter(<Query />);
    expect(screen.getByPlaceholderText('Ask a question about your knowledge base...')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('search button is enabled by default', () => {
    renderWithRouter(<Query />);
    const searchButton = screen.getByText('Search');
    expect(searchButton).not.toBeDisabled();
  });

  it('handles successful query', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        question: 'What is RAG?',
        answer: 'RAG stands for Retrieval-Augmented Generation.',
        sources: [
          { doc_id: 'doc_1', score: 0.95, text_preview: 'RAG is a technique...' },
        ],
        context_chunks: 1,
      }),
    });
    renderWithRouter(<Query />);
    fireEvent.change(screen.getByPlaceholderText('Ask a question about your knowledge base...'), { target: { value: 'What is RAG?' } });
    fireEvent.click(screen.getByText('Search'));
    await waitFor(() => {
      expect(screen.getByText('RAG stands for Retrieval-Augmented Generation.')).toBeInTheDocument();
    });
  });

  it('displays sources with scores', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        question: 'What is RAG?',
        answer: 'RAG stands for Retrieval-Augmented Generation.',
        sources: [
          { doc_id: 'doc_1', score: 0.95, text_preview: 'RAG is a technique...' },
          { doc_id: 'doc_2', score: 0.87, text_preview: 'Generation models...' },
        ],
        context_chunks: 2,
      }),
    });
    renderWithRouter(<Query />);
    fireEvent.change(screen.getByPlaceholderText('Ask a question about your knowledge base...'), { target: { value: 'What is RAG?' } });
    fireEvent.click(screen.getByText('Search'));
    await waitFor(() => {
      expect(screen.getByText('Sources')).toBeInTheDocument();
      expect(screen.getByText('doc_1')).toBeInTheDocument();
      expect(screen.getByText((content) => content.includes('0.95'))).toBeInTheDocument();
      expect(screen.getByText('RAG is a technique...')).toBeInTheDocument();
    });
  });
});