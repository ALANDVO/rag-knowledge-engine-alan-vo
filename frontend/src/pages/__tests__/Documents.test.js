import { jsx as _jsx } from "react/jsx-runtime";
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Documents from '../Documents';
const renderWithRouter = (component) => {
    return render(_jsx(BrowserRouter, { children: component }));
};
describe('Documents', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        global.fetch.mockReset();
    });
    it('renders page title', () => {
        renderWithRouter(_jsx(Documents, {}));
        const titles = screen.getAllByText('Documents');
        expect(titles.length).toBeGreaterThan(0);
    });
    it('shows text ingestion form', () => {
        renderWithRouter(_jsx(Documents, {}));
        expect(screen.getByPlaceholderText('Document title')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Paste document content...')).toBeInTheDocument();
        expect(screen.getByText('Ingest Document')).toBeInTheDocument();
    });
    it('shows file upload form', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ documents: [], count: 0 }),
        });
        renderWithRouter(_jsx(Documents, {}));
        expect(screen.getByText('Upload File')).toBeInTheDocument();
        expect(screen.getByText('Upload Document')).toBeInTheDocument();
        const fileInput = document.querySelector('input[type="file"]');
        expect(fileInput).toBeInTheDocument();
    });
    it('disables ingest button when fields empty', () => {
        renderWithRouter(_jsx(Documents, {}));
        const ingestButton = screen.getByText('Ingest Document');
        expect(ingestButton).toBeDisabled();
    });
    it('enables ingest button when title and content filled', () => {
        renderWithRouter(_jsx(Documents, {}));
        fireEvent.change(screen.getByPlaceholderText('Document title'), { target: { value: 'Test Title' } });
        fireEvent.change(screen.getByPlaceholderText('Paste document content...'), { target: { value: 'Test content' } });
        const ingestButton = screen.getByText('Ingest Document');
        expect(ingestButton).not.toBeDisabled();
    });
    it('shows file name when file selected', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ documents: [], count: 0 }),
        });
        renderWithRouter(_jsx(Documents, {}));
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
            Object.defineProperty(fileInput, 'files', { value: [file] });
            fireEvent.change(fileInput);
            expect(screen.getByText(/Selected: test.txt/)).toBeInTheDocument();
        }
    });
    it('handles successful text ingestion', async () => {
        global.fetch
            .mockResolvedValueOnce({
            ok: true,
            json: async () => ({ documents: [], count: 0 }),
        })
            .mockResolvedValueOnce({
            ok: true,
            json: async () => ({ doc_id: 'doc_1', chunks: 2, status: 'indexed' }),
        })
            .mockResolvedValueOnce({
            ok: true,
            json: async () => ({ documents: ['doc_1'], count: 1 }),
        });
        renderWithRouter(_jsx(Documents, {}));
        fireEvent.change(screen.getByPlaceholderText('Document title'), { target: { value: 'Test' } });
        fireEvent.change(screen.getByPlaceholderText('Paste document content...'), { target: { value: 'Content' } });
        fireEvent.click(screen.getByText('Ingest Document'));
        await waitFor(() => {
            expect(screen.getByText('doc_1')).toBeInTheDocument();
        });
    });
    it('handles ingestion error', async () => {
        global.fetch
            .mockResolvedValueOnce({
            ok: true,
            json: async () => ({ documents: [], count: 0 }),
        })
            .mockResolvedValueOnce({
            ok: false,
            json: async () => ({ detail: 'Failed to ingest' }),
        });
        renderWithRouter(_jsx(Documents, {}));
        fireEvent.change(screen.getByPlaceholderText('Document title'), { target: { value: 'Test' } });
        fireEvent.change(screen.getByPlaceholderText('Paste document content...'), { target: { value: 'Content' } });
        fireEvent.click(screen.getByText('Ingest Document'));
        await waitFor(() => {
            expect(screen.getByText(/Failed to ingest/)).toBeInTheDocument();
        });
    });
    it('shows empty state when no documents', () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ documents: [], count: 0 }),
        });
        renderWithRouter(_jsx(Documents, {}));
        expect(screen.getByText(/No documents yet/)).toBeInTheDocument();
    });
    it('lists documents when available', async () => {
        global.fetch.mockResolvedValue({
            ok: true,
            json: async () => ({ documents: ['doc_1', 'doc_2'], count: 2 }),
        });
        renderWithRouter(_jsx(Documents, {}));
        await waitFor(() => {
            expect(screen.getByText('doc_1')).toBeInTheDocument();
            expect(screen.getByText('doc_2')).toBeInTheDocument();
        });
    });
});
