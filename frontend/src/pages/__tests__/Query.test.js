import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Query from '../Query';
const renderWithRouter = (component) => {
    return render(_jsx(BrowserRouter, { children: component }));
};
describe('Query', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch.mockReset();
    });
    it('renders page title', () => {
        renderWithRouter(_jsx(Query, {}));
        expect(screen.getByText('Query')).toBeInTheDocument();
    });
    it('shows question input', () => {
        renderWithRouter(_jsx(Query, {}));
        expect(screen.getByPlaceholderText('Ask a question about your knowledge base...')).toBeInTheDocument();
        expect(screen.getByText('Search')).toBeInTheDocument();
    });
    it('search button is enabled by default', () => {
        renderWithRouter(_jsx(Query, {}));
        const searchButton = screen.getByText('Search');
        expect(searchButton).not.toBeDisabled();
    });
    it('handles successful query', async () => {
        global.fetch.mockResolvedValue({
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
        renderWithRouter(_jsx(Query, {}));
        fireEvent.change(screen.getByPlaceholderText('Ask a question about your knowledge base...'), { target: { value: 'What is RAG?' } });
        fireEvent.click(screen.getByText('Search'));
        await waitFor(() => {
            expect(screen.getByText('RAG stands for Retrieval-Augmented Generation.')).toBeInTheDocument();
        });
    });
    it('displays sources with scores', async () => {
        global.fetch.mockResolvedValue({
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
        renderWithRouter(_jsx(Query, {}));
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
