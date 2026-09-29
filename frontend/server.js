import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { createProxyMiddleware } from 'http-proxy-middleware';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const API_TARGET = process.env.API_TARGET || 'http://127.0.0.1:8000';

// Proxy /api requests to FastAPI backend
app.use(
  '/api',
  createProxyMiddleware({
    target: API_TARGET,
    changeOrigin: true,
    pathRewrite: (path, req) => req.originalUrl,
  })
);

// Serve static build from dist directory
const distPath = path.join(__dirname, 'dist');
app.use(express.static(distPath));

// Fallback to index.html for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(distPath, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`[GEOINT C2 Node Server] Listening on http://localhost:${PORT}`);
  console.log(`[GEOINT C2 Node Server] Proxying /api -> ${API_TARGET}`);
  console.log(`[GEOINT C2 Node Server] Operating in 100% Air-Gapped Offline Mode`);
});
