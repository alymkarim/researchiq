import { ChangeEvent, DragEvent, useRef, useState } from "react";
import {
  FileText,
  LoaderCircle,
  UploadCloud,
  X,
  Zap,
} from "lucide-react";

interface UploadPanelProps {
  busy: boolean;
  onUpload: (files: File[]) => Promise<void>;
}

export function UploadPanel({ busy, onUpload }: UploadPanelProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function acceptFiles(files: File[]) {
    const pdfs = files.filter(
      (file) =>
        file.type === "application/pdf" ||
        file.name.toLowerCase().endsWith(".pdf"),
    );

    setSelectedFiles((current) => {
      const seen = new Set(current.map((file) => `${file.name}-${file.size}`));
      const next = [...current];

      pdfs.forEach((file) => {
        const key = `${file.name}-${file.size}`;
        if (!seen.has(key)) {
          next.push(file);
          seen.add(key);
        }
      });

      return next;
    });
  }

  function handleInput(event: ChangeEvent<HTMLInputElement>) {
    acceptFiles(Array.from(event.target.files || []));
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    acceptFiles(Array.from(event.dataTransfer.files));
  }

  async function submit() {
    if (!selectedFiles.length || busy) return;
    await onUpload(selectedFiles);
    setSelectedFiles([]);
  }

  return (
    <section className="lab-panel upload-panel" id="upload">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Specimen intake</span>
          <h2>Feed the paper machine</h2>
        </div>
        <span className="panel-number">01</span>
      </div>

      <div
        className={`drop-zone ${dragging ? "dragging" : ""}`}
        onDragEnter={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          multiple
          onChange={handleInput}
          hidden
        />

        <span className="drop-icon">
          <UploadCloud size={35} />
        </span>

        <strong>Drop research papers here</strong>
        <span>or click to browse your suspiciously organised folders</span>
        <small>PDF only · Multiple papers supported</small>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          {selectedFiles.map((file) => (
            <div className="selected-file" key={`${file.name}-${file.size}`}>
              <FileText size={18} />
              <span>
                <strong>{file.name}</strong>
                <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>
              </span>
              <button
                type="button"
                onClick={() =>
                  setSelectedFiles((current) =>
                    current.filter((candidate) => candidate !== file),
                  )
                }
                aria-label={`Remove ${file.name}`}
              >
                <X size={17} />
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        className="primary-button full-width"
        onClick={submit}
        disabled={!selectedFiles.length || busy}
      >
        {busy ? (
          <>
            <LoaderCircle className="spin" size={19} />
            Processing specimen...
          </>
        ) : (
          <>
            <Zap size={19} />
            Begin experiment
          </>
        )}
      </button>
    </section>
  );
}
