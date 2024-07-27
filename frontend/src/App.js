import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        responseType: 'blob',
      });
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
            Diese Seite ermöglicht es Ihnen, CSV-Dateien hochzuladen und Etiketten mit
            den relevanten Informationen zu generieren. Die Etiketten enthalten
            Auftragsnummern, Annahmedaten, Notizen, Kundennamen und Kennzeichen.
          </p>
        </section>
        <section className="upload-section">
          <h2>CSV-Datei hochladen</h2>
          <form id="upload-form" method="post" onSubmit={handleUpload}>
            <div className="dropzone" id="dropzone" onClick={() => document.getElementById('file-input').click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => {
              e.preventDefault();
              const files = e.dataTransfer.files;
              if (files.length > 0) {
                document.getElementById('file-input').files = files;
                setFile(files[0]);
              }
            }}>
              Ziehen Sie die CSV-Datei hierher oder klicken Sie, um sie hochzuladen
              <input type="file" name="file" id="file-input" style={{ display: 'none' }} onChange={handleFileChange} />
            </div>
            <button type="submit">Hochladen</button>
          </form>
        </section>
      </main>
      <footer>
        <p>Entwickelt von [Dein Name] &copy; 2024</p>
      </footer>
    </div>
  );
}

export default App;