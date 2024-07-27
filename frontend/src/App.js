import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    console.log("File selected: ", event.target.files[0]);
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      console.error("No file selected");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log("Uploading file:", file);
      const response = await axios.post('http://backend:8000/upload/', formData, {
        responseType: 'blob',
      });
      console.log("Upload successful:", response);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Etiketten.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setFile(files[0]);
      console.log("File dropped: ", files[0]);
    }
  };

  return (
    <div className="App">
      <header>
        <img src="/logo.png" alt="Firmenlogo" className="logo" />
        <h1>Etiketten-App</h1>
      </header>
      <main>
        <section className="description">
          <h2>Was macht diese Seite?</h2>
          <p>
            Diese Seite erstellt aus einer <strong>Termine (TAB).txt</strong> Datei ein PDF mit Etiketten zum Aufkleben auf die Schlüsselanhänger. Zu nutzen ist hier Avery Zweckform "49x25". Einfach über unseren TKP Planer auf Exportieren - Termine (TAB getrennt) klicken und die heruntergeladene Datei hier hochladen.
          </p>
        </section>
        <section className="upload-section">
          <h2>TXT-Datei hochladen</h2>
          <form id="upload-form" method="post" onSubmit={handleUpload}>
            <div 
              className={`dropzone ${dragging ? 'dragging' : ''}`} 
              id="dropzone" 
              onClick={() => document.getElementById('file-input').click()} 
              onDragOver={handleDragOver} 
              onDragLeave={handleDragLeave} 
              onDrop={handleDrop}
            >
              {file ? `Selected file: ${file.name}` : 'Ziehen Sie die TXT-Datei hierher oder klicken Sie, um sie hochzuladen'}
              <input type="file" name="file" id="file-input" style={{ display: 'none' }} onChange={handleFileChange} />
            </div>
            <button type="submit">Hochladen</button>
          </form>
        </section>
      </main>
      <footer>
        <p>Entwickelt von Christian Strube &copy; 2024</p>
      </footer>
    </div>
  );
}

export default App;