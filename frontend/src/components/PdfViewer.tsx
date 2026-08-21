import { useEffect, useRef, useState, useCallback } from "react";
import {
  ChevronLeft,
  ChevronRight,
  X,
  ZoomIn,
  ZoomOut,
  LoaderCircle,
} from "lucide-react";
import * as pdfjsLib from "pdfjs-dist";
import type { PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

interface PdfViewerProps {
  documentId: number;
  title: string;
  onClose: () => void;
}

export function PdfViewer({ documentId, title, onClose }: PdfViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [pdf, setPdf] = useState<PDFDocumentProxy | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [scale, setScale] = useState(1.5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const renderPage = useCallback(
    async (page: PDFPageProxy, canvas: HTMLCanvasElement) => {
      const viewport = page.getViewport({ scale });
      const context = canvas.getContext("2d");
      if (!context) return;

      canvas.height = viewport.height;
      canvas.width = viewport.width;

      await page.render({
        canvasContext: context,
        viewport,
        canvas,
      }).promise;
    },
    [scale],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadPdf() {
      try {
        setLoading(true);
        setError(null);

        const stored = localStorage.getItem("researchiq-auth");
        let token: string | null = null;
        if (stored) {
          try {
            const parsed = JSON.parse(stored) as { token?: string };
            token = parsed.token || null;
          } catch {
            /* ignore */
          }
        }
        const headers: Record<string, string> = {};
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(`/api/documents/${documentId}/pdf`, { headers });
        if (!response.ok) {
          throw new Error(`Failed to load PDF: ${response.statusText}`);
        }

        const arrayBuffer = await response.arrayBuffer();
        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        const pdfDoc = await loadingTask.promise;

        if (!cancelled) {
          setPdf(pdfDoc);
          setTotalPages(pdfDoc.numPages);
          setCurrentPage(1);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load PDF");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadPdf();

    return () => {
      cancelled = true;
    };
  }, [documentId]);

  useEffect(() => {
    if (!pdf || !canvasRef.current) return;

    let cancelled = false;

    async function render() {
      if (!pdf || cancelled) return;

      try {
        const page = await pdf.getPage(currentPage);
        if (!cancelled && canvasRef.current) {
          await renderPage(page, canvasRef.current);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to render page");
        }
      }
    }

    render();

    return () => {
      cancelled = true;
    };
  }, [pdf, currentPage, renderPage]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      } else if (e.key === "ArrowLeft" && currentPage > 1) {
        setCurrentPage((p) => p - 1);
      } else if (e.key === "ArrowRight" && currentPage < totalPages) {
        setCurrentPage((p) => p + 1);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose, currentPage, totalPages]);

  return (
    <div className="pdf-viewer-overlay">
      <div className="pdf-viewer-header">
        <h3 className="pdf-viewer-title">{title}</h3>
        <div className="pdf-viewer-controls">
          <button
            className="pdf-viewer-btn"
            onClick={() => setScale((s) => Math.max(0.5, s - 0.25))}
            disabled={scale <= 0.5}
            aria-label="Zoom out"
          >
            <ZoomOut size={18} />
          </button>
          <span className="pdf-viewer-zoom">{Math.round(scale * 100)}%</span>
          <button
            className="pdf-viewer-btn"
            onClick={() => setScale((s) => Math.min(3, s + 0.25))}
            disabled={scale >= 3}
            aria-label="Zoom in"
          >
            <ZoomIn size={18} />
          </button>
        </div>
        <button className="pdf-viewer-close" onClick={onClose} aria-label="Close">
          <X size={20} />
        </button>
      </div>

      <div className="pdf-viewer-body" ref={containerRef}>
        {loading && (
          <div className="pdf-viewer-status">
            <LoaderCircle className="spin" size={32} />
            <p>Loading PDF...</p>
          </div>
        )}

        {error && (
          <div className="pdf-viewer-status error">
            <p>{error}</p>
            <button className="pdf-viewer-btn" onClick={onClose}>
              Close
            </button>
          </div>
        )}

        {!loading && !error && (
          <canvas ref={canvasRef} className="pdf-viewer-canvas" />
        )}
      </div>

      {!loading && !error && totalPages > 0 && (
        <div className="pdf-viewer-footer">
          <button
            className="pdf-viewer-btn"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage <= 1}
            aria-label="Previous page"
          >
            <ChevronLeft size={18} />
          </button>
          <span className="pdf-viewer-page">
            {currentPage} / {totalPages}
          </span>
          <button
            className="pdf-viewer-btn"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage >= totalPages}
            aria-label="Next page"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
