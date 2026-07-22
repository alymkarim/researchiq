import { useEffect, useMemo, useRef, useState } from "react";
import {
  analyseDocument,
  comparePapers,
  deleteDocument,
  getDocuments,
  searchPapers,
  uploadDocuments,
} from "./api";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { ComparisonPanel } from "./components/ComparisonPanel";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { PaperVault } from "./components/PaperVault";
import { ResearchConsole } from "./components/ResearchConsole";
import { Toast } from "./components/Toast";
import { UploadPanel } from "./components/UploadPanel";
import type {
  Analysis,
  ComparisonResult,
  DocumentItem,
  SearchResult,
} from "./types";

interface ToastState {
  message: string;
  type: "success" | "error";
}

export default function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analysingId, setAnalysingId] = useState<number | null>(null);
  const [activeDocumentId, setActiveDocumentId] = useState<number | null>(null);
  const [activeAnalysis, setActiveAnalysis] = useState<Analysis | null>(null);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [comparing, setComparing] = useState(false);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);
  const [online, setOnline] = useState(true);

  const uploadRef = useRef<HTMLDivElement>(null);

  const activeDocument = useMemo(
    () => documents.find((document) => document.id === activeDocumentId),
    [documents, activeDocumentId],
  );

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function loadDocuments() {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data);
      setOnline(true);
    } catch (error) {
      setOnline(false);
      showError(error);
    } finally {
      setLoading(false);
    }
  }

  function showError(error: unknown) {
    setToast({
      type: "error",
      message:
        error instanceof Error
          ? error.message
          : "The laboratory experienced an unexplained wobble.",
    });
  }

  function toggleDocument(id: number) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((value) => value !== id)
        : [...current, id],
    );
  }

  async function handleUpload(files: File[]) {
    setUploading(true);
    try {
      const created = await uploadDocuments(files);
      setDocuments((current) => [...created, ...current]);
      setToast({
        type: "success",
        message: `${created.length} specimen${
          created.length === 1 ? "" : "s"
        } safely contained.`,
      });
      setOnline(true);
    } catch (error) {
      showError(error);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: number) {
    const document = documents.find((item) => item.id === id);
    const confirmed = window.confirm(
      `Incinerate "${document?.title || document?.filename || "this paper"}"?`,
    );
    if (!confirmed) return;

    try {
      await deleteDocument(id);
      setDocuments((current) =>
        current.filter((document) => document.id !== id),
      );
      setSelectedIds((current) => current.filter((value) => value !== id));

      if (activeDocumentId === id) {
        setActiveDocumentId(null);
        setActiveAnalysis(null);
      }

      setToast({
        type: "success",
        message: "Specimen successfully incinerated.",
      });
    } catch (error) {
      showError(error);
    }
  }

  async function handleAnalyse(id: number) {
    setAnalysingId(id);
    try {
      const analysis = await analyseDocument(id);
      setActiveDocumentId(id);
      setActiveAnalysis(analysis);

      setDocuments((current) =>
        current.map((document) =>
          document.id === id ? { ...document, analysis } : document,
        ),
      );

      setToast({
        type: "success",
        message: "Analysis complete. The paper has confessed.",
      });
    } catch (error) {
      showError(error);
    } finally {
      setAnalysingId(null);
    }
  }

  async function handleSearch(query: string) {
    setSearching(true);
    try {
      const results = await searchPapers(query, selectedIds);
      setSearchResults(results);
    } catch (error) {
      showError(error);
    } finally {
      setSearching(false);
    }
  }

  async function handleCompare() {
    if (selectedIds.length < 2) return;

    setComparing(true);
    try {
      const result = await comparePapers(selectedIds);
      setComparison(result);
      setToast({
        type: "success",
        message: "Comparison reactor completed without exploding.",
      });
    } catch (error) {
      showError(error);
    } finally {
      setComparing(false);
    }
  }

  function scrollToUpload() {
    document.getElementById("upload")?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }

  return (
    <>
      <Header online={online} />

      <main>
        <Hero
          documentCount={documents.length}
          onUploadClick={scrollToUpload}
        />

        <div className="workspace-grid" ref={uploadRef}>
          <UploadPanel busy={uploading} onUpload={handleUpload} />

          <PaperVault
            documents={documents}
            loading={loading}
            selectedIds={selectedIds}
            analysingId={analysingId}
            onToggle={toggleDocument}
            onAnalyse={handleAnalyse}
            onDelete={handleDelete}
          />
        </div>

        <div className="dashboard-grid">
          <ResearchConsole
            selectedCount={selectedIds.length}
            searching={searching}
            results={searchResults}
            onSearch={handleSearch}
          />

          <AnalysisPanel
            document={activeDocument}
            analysis={activeAnalysis || activeDocument?.analysis}
          />
        </div>

        <ComparisonPanel
          documents={documents}
          selectedIds={selectedIds}
          comparing={comparing}
          result={comparison}
          onCompare={handleCompare}
        />
      </main>

      <footer>
        <span>RESEARCHIQ LAB · BUILT FOR CURIOUS HUMANS</span>
        <span>AI can assist. Evidence still has to do the heavy lifting.</span>
      </footer>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </>
  );
}
