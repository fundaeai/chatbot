import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [file, setFile] = useState(null);
  const [ingestStatus, setIngestStatus] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleIngest = async () => {
    if (!file) return;
    setIngestStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', file);
    try {
      await axios.post('http://localhost:8001/upload', formData);
      setIngestStatus('Uploaded!');
    } catch (err) {
      setIngestStatus(err.response?.data?.detail || err.message || 'Failed');
    }
  };

  const handleAsk = async () => {
    setAnswer('...');
    try {
      const res = await axios.post('http://localhost:8002/ask', { question });
      setAnswer(res.data.answer || JSON.stringify(res.data));
    } catch (err) {
      setAnswer(err.response?.data?.detail || err.message || 'Error');
    }
  };

  const downloadMarkdown = () => {
    const blob = new Blob([answer], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'answer.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #18181b 0%, #b993d6 100%)',
    }}>
      <div style={{ marginBottom: 40, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <input type="file" onChange={handleFileChange} style={{ color: '#fff', marginBottom: 10 }} />
        <button onClick={handleIngest} style={{
          background: 'linear-gradient(90deg, #18181b 0%,rgb(43, 43, 43) 10%)',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          padding: '10px 30px',
          fontSize: 18,
          cursor: 'pointer',
          marginBottom: 8
        }}>Upload</button>
        <div style={{ color: '#fff', minHeight: 24 }}>{ingestStatus}</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          style={{
            width: 250,
            padding: 8,
            borderRadius: 6,
            border: '1px solid #b993d6',
            marginBottom: 10,
            fontSize: 16
          }}
        />
        <button onClick={handleAsk} style={{
          background: 'linear-gradient(90deg, #18181b 0%,rgb(27, 26, 28) 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: 6,
          padding: '10px 30px',
          fontSize: 18,
          cursor: 'pointer',
          marginBottom: 8
        }}>Ask</button>
        <div style={{ color: '#fff', minHeight: 24, textAlign: 'center', maxWidth: 600 }}>
          <ReactMarkdown>{answer}</ReactMarkdown>
        </div>
        {answer && answer !== '...' && (
          <button
            onClick={downloadMarkdown}
            style={{
              background: 'linear-gradient(90deg, #18181b 0%,rgb(31, 26, 34) 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              padding: '8px 20px',
              fontSize: 16,
              cursor: 'pointer',
              marginTop: 10
            }}
          >
            Download as Markdown
          </button>
        )}
      </div>
    </div>
  );
}

export default App; 