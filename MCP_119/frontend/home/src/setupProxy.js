const { createProxyMiddleware } = require('http-proxy-middleware');
module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: (path, req) => path,
      onProxyReq: (proxyReq, req, res) => {
        // In newer Node.js versions, proxyReq.headers may be undefined. Use
        // setHeader to ensure the host header is forwarded correctly.
        proxyReq.setHeader('host', req.headers.host);
      }
    })
  );
};
