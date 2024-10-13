import React, { useState } from 'react';
import { Github, Download, Copy, AlertCircle } from 'lucide-react';

interface FileStructure {
  [key: string]: string | FileStructure;
}

function App() {
  const [token, setToken] = useState('');
  const [url, setUrl] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRepoContent = async () => {
    setLoading(true);
    setError(null);
    setContent('');

    try {
      if (!token.trim()) {
        throw new Error('GitHub token is required');
      }

      if (!url.trim() || !url.includes('github.com')) {
        throw new Error('Invalid GitHub repository URL');
      }

      const urlParts = url.split('/');
      if (urlParts.length < 5) {
        throw new Error('Invalid GitHub repository URL format');
      }

      const owner = urlParts[3];
      const repo = urlParts[4];
      const apiUrl = `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`;

      console.log('Fetching repository content...');
      const response = await fetch(apiUrl, {
        headers: {
          Authorization: `token ${token}`,
        },
      });

      if (!response.ok) {
        console.error('API response not OK:', response.status, response.statusText);
        if (response.status === 401) {
          throw new Error('Invalid GitHub token');
        } else if (response.status === 404) {
          throw new Error('Repository not found');
        } else {
          throw new Error(`Failed to fetch repository content: ${response.statusText}`);
        }
      }

      const data = await response.json();
      console.log('Repository data received:', data);

      const fileStructure: FileStructure = {};

      for (const item of data.tree) {
        if (item.type === 'blob') {
          try {
            const pathParts = item.path.split('/');
            let currentLevel = fileStructure;
            for (let i = 0; i < pathParts.length; i++) {
              const part = pathParts[i];
              if (i === pathParts.length - 1) {
                currentLevel[part] = await fetchFileContent(owner, repo, item.path);
              } else {
                if (!currentLevel[part]) {
                  currentLevel[part] = {};
                }
                currentLevel = currentLevel[part] as FileStructure;
              }
            }
          } catch (fileError) {
            console.error(`Error fetching file content for ${item.path}:`, fileError);
          }
        }
      }

      console.log('File structure created:', fileStructure);

      const formattedContent = `# File Structure\n\n\`\`\`\n${formatFileStructureAscii(fileStructure)}\`\`\`\n\n# File Contents\n\n${formatFileContents(fileStructure)}`;
      setContent(formattedContent);
    } catch (error) {
      console.error('Error fetching repository content:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (owner: string, repo: string, path: string) => {
    console.log(`Fetching file content for ${path}...`);
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;
    const response = await fetch(apiUrl, {
      headers: {
        Authorization: `token ${token}`,
      },
    });
    if (!response.ok) {
      console.error(`Failed to fetch file content for ${path}:`, response.status, response.statusText);
      throw new Error(`Failed to fetch file content: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`File content received for ${path}`);
    return decodeURIComponent(escape(atob(data.content)));
  };

  const formatFileStructureAscii = (structure: FileStructure, prefix = ''): string => {
    let result = '';
    const entries = Object.entries(structure);
    for (let i = 0; i < entries.length; i++) {
      const [key, value] = entries[i];
      const isLast = i === entries.length - 1;
      const newPrefix = prefix + (isLast ? '└── ' : '├── ');
      result += newPrefix + key + '\n';
      if (typeof value !== 'string') {
        const newChildPrefix = prefix + (isLast ? '    ' : '│   ');
        result += formatFileStructureAscii(value, newChildPrefix);
      }
    }
    return result;
  };

  const formatFileContents = (structure: FileStructure, path = ''): string => {
    let result = '';
    for (const [key, value] of Object.entries(structure)) {
      const fullPath = path ? `${path}/${key}` : key;
      if (typeof value === 'string') {
        result += `## ${fullPath}\n\`\`\`\n${value}\n\`\`\`\n\n`;
      } else {
        result += formatFileContents(value, fullPath);
      }
    }
    return result;
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'repo-content.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4 flex items-center">
          <Github className="mr-2" /> GitHub Repository Viewer
        </h1>
        <div className="mb-4">
          <input
            type="text"
            placeholder="GitHub Token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div className="mb-4">
          <input
            type="text"
            placeholder="GitHub Repository URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          onClick={fetchRepoContent}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? 'Loading...' : 'Fetch Repository Content'}
        </button>
        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
            <AlertCircle className="mr-2" />
            {error}
          </div>
        )}
        {content && (
          <div className="mt-4">
            <div className="flex justify-end space-x-2 mb-2">
              <button
                onClick={handleDownload}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 flex items-center"
              >
                <Download className="mr-2" /> Download
              </button>
              <button
                onClick={handleCopy}
                className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 flex items-center"
              >
                <Copy className="mr-2" /> Copy
              </button>
            </div>
            <textarea
              value={content}
              readOnly
              className="w-full h-96 p-2 border rounded font-mono text-sm"
              style={{ whiteSpace: 'pre-wrap', overflowWrap: 'break-word' }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;