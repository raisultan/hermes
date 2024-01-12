import React, { useState, useRef, useEffect, ChangeEvent } from 'react';
import axios from 'axios';

// Define a type for your API response items
type SearchResult = {
  path: string;
  page: number;
  text: string;
};

const App = () => {
  const [folderSelected, setFolderSelected] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const folderInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const selected = localStorage.getItem('folderSelected') === 'true';
    setFolderSelected(selected);

    if (folderInputRef.current) {
      folderInputRef.current.setAttribute('webkitdirectory', '');
      folderInputRef.current.setAttribute('directory', '');
    }
  }, []);

  const handleFolderChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      localStorage.setItem('folderSelected', 'true');
      setFolderSelected(true);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/search', { text: searchTerm });
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const resetSelection = () => {
    localStorage.setItem('folderSelected', 'false');
    setFolderSelected(false);
  };

  return (
    <div>
      {!folderSelected ? (
        <div>
          <label>
            Select folder:
            <input type="file" ref={folderInputRef} onChange={handleFolderChange} />
          </label>
        </div>
      ) : (
        <div>
          <input 
            type="text" 
            value={searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)} 
            placeholder="Enter search term" 
          />
          <button onClick={handleSearch}>Search</button>
          <div>
            {results.map((item, index) => (
              <div key={index}>
                <p>Path: {item.path}</p>
                <p>Page: {item.page}</p>
                <p>Text: {item.text}</p>
              </div>
            ))}
          </div>
          <button onClick={resetSelection}>Reset Folder Selection</button>
        </div>
      )}
    </div>
  );
};

export default App;
