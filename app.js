
var io = require('socket.io');
var server = require('http').createServer();
server.listen(80, "http://vm.public-node-1-128.ch-geni-net.lan.sdn.uky.edu");
var socket = io.listen(server);

io.on('connection', function (socket) {
socket.emit('news', { hello: 'world' });
socket.on('my other event', function (data) {
console.log(data);
  });
});
