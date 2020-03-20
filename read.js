var io = require('socket.io');
var server = require('http').createServer();
server.listen(8001, '0.0.0.0'); //need change port number every time
var sockets = io.listen(server);

//----socket set up-----

var SelfReloadJSON = require('self-reload-json');

const readFile = new SelfReloadJSON({
    fileName: './test.json',
    additive: false,
    delay: 500
  });

readFile.on('updated', () => {
    console.log('File Updated:', readFile);
    setTimeout(() => {
      readFile.save();
    }, 100);
  })
  readFile.on('error', (err) => {
    console.log('Error while refreshing:', err.message || err);
  })


sockets.on('connection', function (socket) {
  console.log('connection start');
  socket.emit('news', { hello: 'world' });//监听，一旦客户端连接上，即发送数据，第一个参数'new'为数据名，第二个参数既为数据  
  console.log('sent sucessfully');
  socket.on('my other event', function (data) {//得到client的 数据名为'my other event' 的数据
  console.log(data.my);
  });
});
