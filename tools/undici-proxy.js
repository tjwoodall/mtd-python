const { setGlobalDispatcher, ProxyAgent } = require('undici');

setGlobalDispatcher(
  new ProxyAgent(process.env.HTTPS_PROXY || process.env.HTTP_PROXY)
);
