import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [startPosition, setStartPosition] = useState({ row: 0, col: 0 });

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/plain') {
        setErrorMessage('Nur .txt Dateien sind erlaubt.');
        return;
      }
      if (selectedFile.size > 300 * 1024) {
        setErrorMessage('Die Datei darf maximal 300 KB groß sein.');
        return;
      }
      setFile(selectedFile);
      setErrorMessage('');
      console.log("File selected: ", selectedFile);
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!file) {
      console.error("No file selected");
      setErrorMessage('Bitte wählen Sie eine Datei aus.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('start_position', JSON.stringify(startPosition));

    try {
      console.log("Uploading file:", file);
      const response = await axios.post('https://etiketten.cstrube.de/upload/', formData, {
        responseType: 'blob',
      });
      console.log("Upload successful:", response);

      const contentDisposition = response.headers['content-disposition'];
      let filename = 'Etiketten.pdf';
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="(.+)"/);
        if (matches.length > 1) {
          filename = matches[1];
        }
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      setFile(null);
      document.getElementById('file-input').value = '';
    } catch (error) {
      console.error('Error uploading file:', error);
      setErrorMessage('Fehler beim Hochladen der Datei.');
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
      const selectedFile = files[0];
      if (selectedFile.type !== 'text/plain') {
        setErrorMessage('Nur .txt Dateien sind erlaubt.');
        return;
      }
      if (selectedFile.size > 300 * 1024) {
        setErrorMessage('Die Datei darf maximal 300 KB groß sein.');
        return;
      }
      setFile(selectedFile);
      setErrorMessage('');
      console.log("File dropped: ", selectedFile);
    }
  };

  const handleCellClick = (row, col) => {
    setStartPosition({ row, col });
  };

  return (
    <div className="App">
      <header>
        <img src="/logo.png" alt="Firmenlogo" className="logo" />
        <h1>Etiketten-App</h1>
      </header>
      <main>
        <section className="description">
          <h2>Was macht diese App?</h2>
          <p>
          Diese Anwendung generiert aus einer Datei im Format Termine (TAB).txt ein PDF-Dokument mit Etiketten, die auf Schlüsselanhänger aufgeklebt werden können. Für diesen Zweck verwenden Sie bitte Avery Zweckform Typ 3657 “49x25”. Um die Datei zu erstellen, wählen Sie in unserem TKP Planer die Option “Exportieren - Termine (TAB getrennt)” und laden Sie die heruntergeladene Datei hier hoch.
          </p>
        </section>
        <section className="upload-section">
          <h2>Termine (TAB).txt - Datei hochladen</h2>
          {errorMessage && <p className="error-message">{errorMessage}</p>}
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
            <div className="matrix">
              {Array.from({ length: 10 }).map((_, row) => (
                <div key={row} className="matrix-row">
                  {Array.from({ length: 4 }).map((_, col) => (
                    <div 
                      key={col} 
                      className={`matrix-cell ${startPosition.row === row && startPosition.col === col ? 'selected' : ''}`} 
                      onClick={() => handleCellClick(row, col)}
                    />
                  ))}
                </div>
              ))}
            </div>
            <button type="submit">Etiketten erstellen</button>
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