import { useState } from "react";
import { Copy, LoaderCircle, Share2, Check } from "lucide-react";
import { createShare } from "../api";

interface ShareButtonProps {
  selectedIds: number[];
}

export function ShareButton({ selectedIds }: ShareButtonProps) {
  const [loading, setLoading] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function handleShare() {
    if (selectedIds.length === 0) return;

    setLoading(true);
    setShareUrl(null);

    try {
      const result = await createShare(selectedIds);
      const url = `${window.location.origin}/shared/${result.share_id}`;
      setShareUrl(url);
    } catch {
      setShareUrl(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  }

  if (selectedIds.length === 0) return null;

  return (
    <div className="share-section">
      <button className="share-btn" onClick={handleShare} disabled={loading}>
        {loading ? (
          <LoaderCircle className="spin" size={16} />
        ) : (
          <Share2 size={16} />
        )}
        Share {selectedIds.length} paper{selectedIds.length !== 1 ? "s" : ""}
      </button>

      {shareUrl && (
        <div className="share-result">
          <input className="share-url" value={shareUrl} readOnly />
          <button className="share-copy" onClick={handleCopy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </button>
        </div>
      )}
    </div>
  );
}
