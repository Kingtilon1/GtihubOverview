"use client";

import ReactMarkdown from "react-markdown";
import { useState } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  createTheme,
  ThemeProvider,
} from "@mui/material";

// Create a custom theme based on GitHub's dark mode
const githubTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#24292e", // GitHub's primary color
    },
    secondary: {
      main: "#f9826c", // GitHub's secondary color
    },
    background: {
      default: "#0d1117", // GitHub's dark background color
      paper: "#161b22", // GitHub's card background color
    },
  },
});

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [repoProcessed, setRepoProcessed] = useState(false);
  const [typingAnswer, setTypingAnswer] = useState("");

  // First process the repo
  const processRepo = async () => {
    setLoading(true);
    setLoadingMessage("Processing repository...");
    setError(null);
    try {
      const response = await fetch("http://127.0.0.1:5000/repo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to process repository");
      }

      console.log("Repo processed:", data);
      setRepoProcessed(true);
    } catch (err) {
      console.error("Error processing repo:", err);
      setError(err.message);
    } finally {
      setLoadingMessage("");
      setLoading(false);
    }
  };

  // Then handle questions
  const handleAskQuestion = async (e) => {
    e.preventDefault();
    setLoading(true);
    setLoadingMessage("Fetching answer...");
    setError(null);
    try {
      const response = await fetch("http://127.0.0.1:5000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question, repo_url: repoUrl }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to get answer");
      }

      setResponse(data);
      startTypingEffect(data.answer);
    } catch (err) {
      console.error("Error getting answer:", err);
      setError(err.message);
    } finally {
      setLoadingMessage("");
      setLoading(false);
    }
  };

  //for typing effect
  const startTypingEffect = (text) => {
    let index = 0;
    const interval = setInterval(() => {
      setTypingAnswer(text.slice(0, index + 1));
      index++;
      if (index >= text.length) {
        clearInterval(interval);
      }
    }, 50);
  };

  return (
    <ThemeProvider theme={githubTheme}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          bgcolor: "background.default",
          color: "text.primary",
          padding: 4,
        }}
      >
        <Box
          sx={{
            width: "100%",
            maxWidth: 600,
            padding: 4,
            borderRadius: 2,
            bgcolor: "background.paper",
            boxShadow: "0 0 20px rgba(0, 0, 0, 0.1)",
          }}
        >
          <Typography variant="h4" gutterBottom>
            GitHub Repository Q&A
          </Typography>

          {error && (
            <Typography color="secondary" sx={{ mb: 2 }}>
              Error: {error}
            </Typography>
          )}

          <TextField
            fullWidth
            label="GitHub Repository URL"
            variant="outlined"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            sx={{ mb: 2 }}
            slotProps={{
              input: {
                style: {
                  color: "white",
                },
              },
            }}
          />

          <Button
            fullWidth
            variant="contained"
            onClick={processRepo}
            disabled={!repoUrl || loading}
            sx={{ mb: 2 }}
          >
            {loading ? (
              <CircularProgress size={24} color="secondary" />
            ) : (
              "Process Repository"
            )}
          </Button>

          {repoProcessed && (
            <>
              <TextField
                fullWidth
                label="Your Question"
                variant="outlined"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                sx={{ mb: 2 }}
                slotProps={{
                  input: {
                    style: {
                      color: "white",
                    },
                  },
                }}
              />

              <Button
                fullWidth
                variant="contained"
                onClick={handleAskQuestion}
                disabled={!question || loading}
              >
                {loading ? (
                  <CircularProgress size={24} color="secondary" />
                ) : (
                  "Ask Question"
                )}
              </Button>
            </>
          )}

          {loading && (
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <CircularProgress size={24} color="secondary" />
              <Typography sx={{ ml: 2 }}>{loadingMessage}</Typography>
            </Box>
          )}
          {response && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6">Answer:</Typography>
              <ReactMarkdown
                components={{
                  p: ({ node, ...props }) => <Typography {...props} />,
                }}
              >
                {typingAnswer}
              </ReactMarkdown>
              <Typography variant="h6" sx={{ mt: 2 }}>
                Sections:
              </Typography>
              <Typography>{response.sources?.join(", ")}</Typography>
            </Box>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}
