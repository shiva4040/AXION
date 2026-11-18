import React, { useEffect, useState } from 'react';
import { BookOpen, Upload, FileText, CheckCircle, Shield, AlertCircle } from 'lucide-react';
import { getDocuments, ingestText } from '../../api/client';
import { DocumentSummary } from '../../types';

export const KnowledgeLibrary: React.FC = () => {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadText, setUploadText] = useState('');
  const [uploadTrust, setUploadTrust] = useState('PEER_REVIEWED');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocs(data);
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadTitle.trim() || !uploadText.trim()) return;
    setUploading(true);
    setMessage(null);
    try {
      await ingestText(uploadTitle, uploadText, `manual://${uploadTitle.replace(/\s+/g, '_')}`, uploadTrust);
      setUploadTitle('');
      setUploadText('');
      setMessage('Document successfully ingested and indexed.');
      await loadDocs();
    } catch (err: any) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-2">
        <BookOpen className="w-5 h-5 text-emerald-600" />
        <h1 className="text-xl font-bold text-gray-900">Knowledge Library</h1>
      </div>
      <p className="text-xs text-gray-500 mb-6">
        Manage scientific literature, research papers, and technical documents indexed into AXION’s verifiable knowledge base.
      </p>

      {/* Ingestion Card */}
      <div className="p-5 bg-white border border-gray-200 rounded-2xl shadow-xs mb-8">
        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
          <Upload className="w-3.5 h-3.5 text-blue-600" />
          Ingest Scientific Text or Paper Excerpt
        </h2>
        <form onSubmit={handleIngest} className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <input
              type="text"
              placeholder="Document Title (e.g., Navier-Stokes Continuum Transport)"
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
              className="sm:col-span-2 text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
              required
            />
            <select
              value={uploadTrust}
              onChange={(e) => setUploadTrust(e.target.value)}
              className="text-xs border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-blue-500"
            >
              <option value="PEER_REVIEWED">Peer-Reviewed Journal</option>
              <option value="PREPRINT">Preprint (arXiv/bioRxiv)</option>
              <option value="TEXTBOOK">Authoritative Textbook</option>
              <option value="UNVERIFIED">Unverified / Working Draft</option>
            </select>
          </div>
          <textarea
            rows={4}
            placeholder="Paste raw paper text, equations, or abstract content..."
            value={uploadText}
            onChange={(e) => setUploadText(e.target.value)}
            className="w-full text-xs border border-gray-200 rounded-lg p-3 focus:outline-none focus:border-blue-500 font-mono"
            required
          />
          <div className="flex items-center justify-between">
            {message && (
              <span className={`text-xs ${message.startsWith('Error') ? 'text-red-600' : 'text-emerald-600'}`}>
                {message}
              </span>
            )}
            <button
              type="submit"
              disabled={uploading}
              className="ml-auto text-xs font-semibold px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {uploading ? 'Ingesting...' : 'Ingest & Chunk'}
            </button>
          </div>
        </form>
      </div>

      {/* Document Table */}
      <h2 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
        Indexed Documents ({docs.length})
      </h2>
      {loading ? (
        <div className="text-xs text-gray-400 py-8 text-center">Loading documents...</div>
      ) : docs.length === 0 ? (
        <div className="p-8 bg-gray-50 border border-gray-200 rounded-xl text-center text-xs text-gray-500">
          No documents ingested yet. Use the ingestion form above to add scientific sources.
        </div>
      ) : (
        <div className="space-y-2.5">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className="p-4 bg-white border border-gray-200 rounded-xl flex items-center justify-between text-xs shadow-2xs hover:border-gray-300 transition-colors"
            >
              <div className="flex items-start gap-3">
                <FileText className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-900">{doc.title}</h4>
                  <div className="text-[11px] text-gray-500 font-mono mt-0.5">
                    URI: {doc.source_uri} &bull; Pages: {doc.page_count}
                  </div>
                  <div className="text-[10px] text-gray-400 font-mono">
                    SHA256: {doc.file_hash_sha256 ? `${doc.file_hash_sha256.substring(0, 16)}...` : 'N/A'}
                  </div>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-100 uppercase tracking-wider">
                {doc.trust_tier}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
