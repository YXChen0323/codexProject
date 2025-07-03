const { createProxyMiddleware } = require('http-proxy-middleware');
module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: (path, req) => path,
      onProxyReq: (proxyReq, req, res) => {
        Object.assign(proxyReq.headers, { host: req.headers.host });
      }
    })
  );
};
