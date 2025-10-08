import React, { useState } from 'react';
import { Controlled as CodeMirror } from 'react-codemirror2';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/material.css';
import 'codemirror/mode/clike/clike';
import { Button, Container, Typography, Box, Paper } from '@mui/material';

function App() {
  const [code, setCode] = useState(`#include <stdio.h>
int main() {
    int x = 0;
    if (x < 5) {
        printf("x is less than 5\\n");
        x++;
    }
    return x;
}`);
  const [astImage, setAstImage] = useState(null);
  const [error, setError] = useState(null);

  const parseCode = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5050/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Response data:', data); // Debug: Log the response
      if (data.image) {
        setAstImage(data.image); // Set the base64 image string
        setError(null);
      } else if (data.error) {
        setError(data.error);
      } else {
        setError('Unexpected response format');
      }
    } catch (error) {
      setError(`Failed to fetch AST: ${error.message}`);
      console.error('Fetch error:', error); // Debug: Log the error
    }
  };

  return (
    <Container maxWidth={false}>
      <Box my={4}>
        <Typography variant="h3" align="center" gutterBottom>
          C Code AST Visualizer
        </Typography>
        <Typography variant="subtitle1" align="center" color="textSecondary">
          Input your C code to see its Abstract Syntax Tree!
        </Typography>
      </Box>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <CodeMirror
          value={code}
          options={{
            mode: 'text/x-csrc',
            theme: 'material',
            lineNumbers: true,
            autoCursor: true,
          }}
          onBeforeChange={(editor, data, value) => setCode(value)}
          editorDidMount={(editor) => {
            editor.setSize('100%', '400px');
          }}
        />
      </Paper>
      <Box mb={2} textAlign="center">
        <Button variant="contained" color="primary" onClick={parseCode}>
          Parse Code
        </Button>
      </Box>
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}
      {astImage && (
        <Box mt={4} textAlign="center">
          <img
            src={astImage}
            alt="AST Visualization"
            style={{ maxWidth: '100%', height: 'auto', border: '1px solid #ddd' }}
            onError={() => setError('Failed to load image')}
          />
        </Box>
      )}
    </Container>
  );
}

export default App;