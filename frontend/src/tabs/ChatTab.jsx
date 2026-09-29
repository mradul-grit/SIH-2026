import React, { useState, useRef, useEffect } from 'react';
import { Icon } from '../components/Icons';

export const ChatTab = () => {
  const [messages, setMessages] = useState([
    {
      id: 'init-1',
      sender: 'assistant',
      author: 'GEOINT Tactical Agent',
      timestamp: 'SYSTEM ONLINE',
      markdown: `### 🛰️ SIH-227 Tactical Multimodal Intelligence Terminal

Welcome, Tactical Analyst. This system operates **100% locally and offline** on local edge hardware with zero external API dependencies.

#### Operational Capabilities:
* **Single-Tile Reconnaissance (1 Image)**: Attach 1 observation to inspect land cover, roads, structural footprints, water bodies, or verify physical atmospheric conditions.
* **Bi-Temporal Change Analysis (2 Images)**: Attach $T_1$ and $T_2$ observations to run native-resolution change detection, count structural clusters, and suppress false alarms.
* **Direct Tactical Question Answering**: Query physical features directly (e.g. animals, water bodies, clouds, or infrastructure) for immediate verified answers.`
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [modelType, setModelType] = useState('siamese_resnet18_cbam');
  const streamEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    files.slice(0, 2 - attachments.length).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (loadEvt) => {
        setAttachments((prev) => [
          ...prev,
          { file, base64: loadEvt.target.result, name: file.name }
        ]);
      };
      reader.readAsDataURL(file);
    });
    e.target.value = '';
  };

  const removeAttachment = (idx) => {
    setAttachments((prev) => prev.filter((_, i) => i !== idx));
  };

  const loadSampleTile = async (sampleId, defaultText) => {
    try {
      const res = await fetch(`/api/sample-pair/${sampleId}`);
      if (!res.ok) throw new Error('Sample not found');
      const data = await res.json();

      // Convert dataURI to File
      const resBlob = await fetch(data.t1_base64);
      const blob = await resBlob.blob();
      const file = new File([blob], `${data.filename}_T1.png`, { type: 'image/png' });

      setAttachments([{ file, base64: data.t1_base64, name: `${data.filename} (Single Recon)` }]);
      setInputQuery(defaultText || 'Is there any animal, cloud, or water body in this image?');
    } catch (err) {
      alert('Error loading sample: ' + err.message);
    }
  };

  const loadSamplePair = async (sampleId, defaultText) => {
    try {
      const res = await fetch(`/api/sample-pair/${sampleId}`);
      if (!res.ok) throw new Error('Sample not found');
      const data = await res.json();

      const blob1 = await (await fetch(data.t1_base64)).blob();
      const file1 = new File([blob1], `${data.filename}_T1.png`, { type: 'image/png' });

      const blob2 = await (await fetch(data.t2_base64)).blob();
      const file2 = new File([blob2], `${data.filename}_T2.png`, { type: 'image/png' });

      setAttachments([
        { file: file1, base64: data.t1_base64, name: `${data.filename} (T1)` },
        { file: file2, base64: data.t2_base64, name: `${data.filename} (T2)` }
      ]);
      setInputQuery(defaultText || `Analyze structural and building changes between T1 and T2 for ${data.filename}.`);
    } catch (err) {
      alert('Error loading sample pair: ' + err.message);
    }
  };

  const submitQuery = async () => {
    const q = inputQuery.trim();
    if (!q && attachments.length === 0) return;

    const userMsg = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      author: 'Tactical Analyst',
      timestamp: new Date().toLocaleTimeString(),
      query: q || '[Submitted image(s) for tactical evaluation]',
      attachedImages: [...attachments]
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    const currentAtts = [...attachments];
    setAttachments([]);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('query', q);
      formData.append('threshold', '0.40');
      formData.append('model_type', modelType);

      currentAtts.forEach((att) => {
        formData.append('files', att.file);
      });

      const res = await fetch('/api/chat-query', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();

      const assistantMsg = {
        id: `ai-${Date.now()}`,
        sender: 'assistant',
        author: 'GEOINT Tactical Agent',
        timestamp: new Date().toLocaleTimeString(),
        markdown: data.answer_markdown || 'Analysis completed.',
        metrics: data.metrics || null,
        visuals: data.visuals || null,
        suggestedFollowups: data.suggested_followups || []
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        author: 'SYSTEM WARNING',
        timestamp: new Date().toLocaleTimeString(),
        markdown: `> **COMMUNICATION ERROR**: Unable to process request: ${err.message}`
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    const elements = [];

    let currentList = [];

    lines.forEach((line, idx) => {
      const trimmed = line.trim();

      if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        const itemText = trimmed.substring(2);
        currentList.push(<li key={`li-${idx}`} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(itemText) }} />);
        return;
      }

      if (currentList.length > 0) {
        elements.push(<ul key={`ul-${idx}`}>{currentList}</ul>);
        currentList = [];
      }

      if (trimmed.startsWith('### ')) {
        elements.push(<h3 key={idx}>{trimmed.substring(4)}</h3>);
      } else if (trimmed.startsWith('#### ')) {
        elements.push(<h4 key={idx}>{trimmed.substring(5)}</h4>);
      } else if (trimmed.startsWith('> ')) {
        elements.push(<blockquote key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(trimmed.substring(2)) }} />);
      } else if (trimmed === '---') {
        elements.push(<hr key={idx} style={{ borderColor: 'var(--border-subtle)', margin: '10px 0' }} />);
      } else if (trimmed.length > 0) {
        elements.push(<p key={idx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(trimmed) }} />);
      }
    });

    if (currentList.length > 0) {
      elements.push(<ul key={`ul-end`}>{currentList}</ul>);
    }

    return elements;
  };

  const formatInlineMarkdown = (str) => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code style="background:rgba(255,255,255,0.08); padding:1px 4px; border-radius:2px; font-family:var(--font-mono);">$1</code>');
  };

  return (
    <div className="view-body" style={{ height: 'calc(100vh - 108px)', padding: '16px' }}>
      <div className="chat-terminal-wrap">
        {/* Terminal Header Bar */}
        <div style={{ padding: '8px 16px', background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--c2-emerald)', display: 'inline-block' }}></span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 700, color: 'var(--c2-cyan)' }}>
              GEOINT RECONNAISSANCE TERMINAL // C2
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>MODEL:</span>
            <select
              className="c2-select"
              style={{ padding: '3px 8px', fontSize: '11px' }}
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
            >
              <option value="siamese_resnet18_cbam">Siamese ResNet-18 + CBAM</option>
              <option value="changeformer">Lightweight ChangeFormer</option>
            </select>
            <button
              className="c2-btn c2-btn-secondary"
              style={{ padding: '3px 8px', fontSize: '11px' }}
              onClick={() => setMessages([messages[0]])}
            >
              Clear
            </button>
          </div>
        </div>

        {/* Chat History Stream */}
        <div className="chat-history-stream">
          {messages.map((msg) => (
            <div key={msg.id} className={`chat-msg-row ${msg.sender}`}>
              <div className={`msg-callsign ${msg.sender === 'assistant' ? 'ai' : 'user'}`}>
                {msg.sender === 'assistant' ? 'AI' : 'AN'}
              </div>

              <div className="msg-bubble" style={{ maxWidth: '90%' }}>
                <div className="msg-meta">
                  <span className="author">{msg.author}</span>
                  <span>&bull;</span>
                  <span className="mono-nums">{msg.timestamp}</span>
                </div>

                {/* Attached Images Preview in User Message */}
                {msg.attachedImages && msg.attachedImages.length > 0 && (
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                    {msg.attachedImages.map((att, i) => (
                      <div key={i} style={{ border: '1px solid var(--border-default)', borderRadius: '3px', overflow: 'hidden' }}>
                        <img src={att.base64} alt={att.name} style={{ width: '70px', height: '70px', objectFit: 'cover', display: 'block' }} />
                        <div style={{ background: '#000', color: 'var(--c2-cyan)', fontSize: '9px', padding: '1px 4px', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
                          {msg.attachedImages.length === 2 ? (i === 0 ? 'T1' : 'T2') : 'Recon'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {msg.query && <div style={{ marginBottom: '4px' }}>{msg.query}</div>}

                {msg.markdown && (
                  <div className="sitrep-body">
                    {renderMarkdown(msg.markdown)}
                  </div>
                )}

                {/* Visual Imagery Gallery from Dual-Image Change Detection */}
                {msg.visuals && (
                  <div style={{ marginTop: '12px', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--c2-cyan)', marginBottom: '8px' }}>
                      GENERATED SENSOR PRODUCTS:
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
                      {msg.visuals.t1_base64 && (
                        <div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>T1 Pass</div>
                          <img src={msg.visuals.t1_base64} alt="T1" style={{ width: '100%', height: '110px', objectFit: 'cover', border: '1px solid var(--border-subtle)', borderRadius: '2px' }} />
                        </div>
                      )}
                      {msg.visuals.t2_base64 && (
                        <div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>T2 Pass</div>
                          <img src={msg.visuals.t2_base64} alt="T2" style={{ width: '100%', height: '110px', objectFit: 'cover', border: '1px solid var(--border-subtle)', borderRadius: '2px' }} />
                        </div>
                      )}
                      {msg.visuals.mask_base64 && (
                        <div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>Predicted Mask</div>
                          <img src={msg.visuals.mask_base64} alt="Mask" style={{ width: '100%', height: '110px', objectFit: 'cover', border: '1px solid var(--border-subtle)', borderRadius: '2px' }} />
                        </div>
                      )}
                      {msg.visuals.overlay_base64 && (
                        <div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>Change Overlay</div>
                          <img src={msg.visuals.overlay_base64} alt="Overlay" style={{ width: '100%', height: '110px', objectFit: 'cover', border: '1px solid var(--border-subtle)', borderRadius: '2px' }} />
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="chat-msg-row assistant">
              <div className="msg-callsign ai">AI</div>
              <div className="msg-bubble">
                <div className="msg-meta">
                  <span className="author">GEOINT Engine</span>
                  <span>&bull;</span>
                  <span>PROCESSING ON RTX 3050 CUDA...</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--c2-cyan)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                  <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: 'var(--c2-cyan)', animation: 'pulse 1s infinite' }}></span>
                  Computing native inference &amp; physical spectral verification...
                </div>
              </div>
            </div>
          )}
          <div ref={streamEndRef} />
        </div>

        {/* Input & Attachment Dock */}
        <div className="chat-dock">
          {/* Quick Tactical Prompt Chips */}
          <div className="quick-tactical-row">
            <button className="quick-tactical-chip" onClick={() => loadSampleTile('levir_test_1', 'Is there any animal in this image?')}>
              🐾 Check Animals (test_1)
            </button>
            <button className="quick-tactical-chip" onClick={() => loadSampleTile('levir_test_1', 'Are there clouds and water bodies in this image?')}>
              🌊 Check Clouds &amp; Water (test_1)
            </button>
            <button className="quick-tactical-chip" onClick={() => loadSamplePair('levir_test_10')}>
              ⚡ 2 Tiles Change (test_10)
            </button>
            <button className="quick-tactical-chip" onClick={() => loadSamplePair('levir_test_100')}>
              🏢 Commercial Complex (test_100)
            </button>
            <button className="quick-tactical-chip" onClick={() => setInputQuery('Analyze land cover, roads, and structures in this scene')}>
              🗺️ Land Cover Recon
            </button>
            <button className="quick-tactical-chip" onClick={() => setInputQuery('Explain how false alarm suppression works in this air-gapped system')}>
              🛡️ False Alarm Specs
            </button>
          </div>

          {/* Attachments Preview Bar */}
          {attachments.length > 0 && (
            <div className="attachment-preview-dock">
              {attachments.map((att, idx) => (
                <div key={idx} className="attachment-chip">
                  <img src={att.base64} alt={att.name} />
                  <span>{att.name}</span>
                  <button
                    onClick={() => removeAttachment(idx)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                  >
                    <Icon name="x" size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Text Input Row */}
          <div className="chat-input-controls">
            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />

            <button
              className="c2-btn c2-btn-secondary"
              style={{ padding: '8px 10px' }}
              title="Attach Satellite Image (1 for Reconnaissance, 2 for T1/T2 Change Detection)"
              onClick={() => fileInputRef.current?.click()}
            >
              <Icon name="paperclip" size={14} />
            </button>

            <button
              className="c2-btn c2-btn-secondary"
              style={{ padding: '8px 10px', fontSize: '11px' }}
              title="Attach single test tile for VQA"
              onClick={() => loadSampleTile('levir_test_1')}
            >
              1 Tile
            </button>

            <button
              className="c2-btn c2-btn-secondary"
              style={{ padding: '8px 10px', fontSize: '11px' }}
              title="Attach benchmark pair for change detection"
              onClick={() => loadSamplePair('levir_test_10')}
            >
              2 Tiles
            </button>

            <textarea
              className="chat-textarea"
              rows={1}
              placeholder="Ask a question about the attached satellite imagery or enter a tactical query... (Enter to send, Shift+Enter for newline)"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  submitQuery();
                }
              }}
            />

            <button
              className="c2-btn c2-btn-primary"
              style={{ padding: '8px 16px' }}
              disabled={isProcessing || (!inputQuery.trim() && attachments.length === 0)}
              onClick={submitQuery}
            >
              <Icon name="send" size={13} />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
