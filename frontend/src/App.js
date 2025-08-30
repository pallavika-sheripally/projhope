import React, { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [tone, setTone] = useState('neutral');
  const [voice, setVoice] = useState('en-US_AllisonV3Voice');
  const [isProcessing, setIsProcessing] = useState(false);
  const [rewrittenText, setRewrittenText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [showComparison, setShowComparison] = useState(false);
  const [pdfText, setPdfText] = useState('');

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        setPdfText(data.extracted_text);
        setText(data.extracted_text);
        alert('PDF text extracted successfully!');
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error uploading PDF:', error);
      alert('Failed to upload PDF');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    
    setIsProcessing(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/generate-audiobook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text, tone, voice }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setRewrittenText(data.rewritten_text);
        setAudioUrl(`http://localhost:5000${data.audio_url}`);
        setShowComparison(true);
      } else {
        console.error('Error:', data.error);
        alert('Failed to generate audiobook: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate audiobook');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadAudio = () => {
    if (audioUrl) {
      const a = document.createElement('a');
      a.href = audioUrl;
      a.download = 'echoverse-audiobook.mp3';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <h1>EchoVerse</h1>
          <p>AI-Powered Audiobook Creation</p>
        </div>
        
        <div className="content">
          <div className="visualization">
            <div className="book-animation">
              <div className={`book ${isProcessing ? 'processing' : ''}`}>
                <div className="book-cover">
                  <h3>EchoVerse</h3>
                </div>
              </div>
            </div>
          </div>
          
          <div className="controls">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="pdf-upload">Upload PDF:</label>
                <input
                  type="file"
                  id="pdf-upload"
                  accept=".pdf"
                  onChange={handlePdfUpload}
                  style={{display: 'none'}}
                />
                <label htmlFor="pdf-upload" className="upload-btn">
                  📄 Choose PDF File
                </label>
                {pdfText && <span style={{color: 'green', marginLeft: '10px'}}>✓ PDF loaded</span>}
              </div>

              <div className="form-group">
                <label htmlFor="text">Or paste your text:</label>
                <textarea
                  id="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste your text here or upload a PDF above..."
                  rows="8"
                  required
                ></textarea>
              </div>
              
              <div className="form-group">
                <label htmlFor="tone">Select tone:</label>
                <select
                  id="tone"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                >
                  <option value="neutral">Neutral</option>
                  <option value="suspenseful">Suspenseful</option>
                  <option value="inspiring">Inspiring</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="voice">Select voice:</label>
                <select
                  id="voice"
                  value={voice}
                  onChange={(e) => setVoice(e.target.value)}
                >
                  <option value="en-US_AllisonV3Voice">Allison (US English)</option>
                  <option value="en-US_LisaV3Voice">Lisa (US English)</option>
                  <option value="en-US_MichaelV3Voice">Michael (US English)</option>
                </select>
              </div>
              
              <button type="submit" disabled={isProcessing}>
                {isProcessing ? 'Generating...' : 'Generate Audiobook'}
              </button>
            </form>
            
            {audioUrl && (
              <div className="audio-controls">
                <audio controls src={audioUrl} className="audio-player"></audio>
                <button onClick={downloadAudio} className="download-btn">
                  Download MP3
                </button>
              </div>
            )}
          </div>
        </div>
        
        {showComparison && (
          <div className="comparison">
            <h2>Text Comparison</h2>
            <div className="comparison-content">
              <div className="original">
                <h3>Original Text</h3>
                <p>{text}</p>
              </div>
              <div className="rewritten">
                <h3>Tone-Adapted Text</h3>
                <p>{rewrittenText}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;