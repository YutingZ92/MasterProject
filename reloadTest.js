
  const SelfReloadJSON = require('self-reload-json');
  
  const watchFile = new SelfReloadJSON({
    fileName: './node_modules/self-reload-json/test.json',
    additive: false,
    delay: 500
  });
  console.log('File content:', Object.keys(watchFile)[0]);
  watchFile.on('updated', () => {
    console.log('File Updated:', watchFile);
    setTimeout(() => {
      watchFile.save();
    }, 100);
  })
  watchFile.on('error', (err) => {
    console.log('Error while refreshing:', err.message || err);
  })

