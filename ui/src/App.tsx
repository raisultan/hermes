import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App: React.FC = () => {
  const [dirPath, setDirPath] = useState<string | null>(null);
  const [inputDirPath, setInputDirPath] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isPathSet, setIsPathSet] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/dir_path')
      .then(response => {
        if (response.status === 204) {
          setIsPathSet(false);
        } else if (response.data.dir_path) {
          setDirPath(response.data.dir_path);
          setIsPathSet(true);
        }
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching the directory path', error);
        setIsLoading(false);
      });
  }, []);

  const handleDirPathChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputDirPath(event.target.value);
  };

  const handleDirSelection = async () => {
    if (!inputDirPath) {
      console.error('No directory path provided');
      return;
    }

    try {
      await axios.post('http://127.0.0.1:8000/api/dir_path', { dir_path: inputDirPath });
      setDirPath(inputDirPath);
      setIsPathSet(true);
    } catch (error) {
      console.error('Error setting the directory path', error);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      {isPathSet ? (
        <div>
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search PDFs..."
          />
          <button>Search</button>
        </div>
      ) : (
        <div>
          <input
            type="text"
            value={inputDirPath}
            onChange={handleDirPathChange}
            placeholder="Enter directory path"
          />
          <button onClick={handleDirSelection}>Set PDF Directory</button>
        </div>
      )}
    </div>
  );
};

export default App;
