
var io = require('socket.io');
var server = require('http').createServer();
//server.listen(80,"http://128.163.232.70");
server.listen(80);
var sockets = io.listen(server);

sockets.on('connection', function (socket) {
socket.emit('news', { hello: 'world' });//监听，一旦客户端连接上，即发送数据，第一个参数'new'为数据名，第二个参数既为数据  
socket.on('my other event', function (data) {//得到client的 数据名为'my other event' 的数据
console.log(data.my);
  });
});
