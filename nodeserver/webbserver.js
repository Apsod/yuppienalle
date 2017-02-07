// Here should be the code from the example for the webserver, webserver.js,
// you need that also.

// Require the modules we need
var WebSocketServer = require('websocket').server;

// Create an object for the websocket
// <a href='https://github.com/Worlize/WebSocket-Node/wiki/Documentation'>https://github.com/Worlize/WebSocket-Node/wiki/Documentation</a>
wsServer = new WebSocketServer({
  httpServer: httpServer,
  autoAcceptConnections: false
});

// Create a callback to handle each connection request
wsServer.on('request', function(request) {
  var connection = request.accept();
  console.log((new Date()) + ' Connection accepted from ' + request.origin);

  // Callback to handle each message from the client
  connection.on('message', function(message) {
      if (message.type === 'utf8') {
          console.log('Received Message: ' + message.utf8Data);
          connection.sendUTF(message.utf8Data);
      }
      else if (message.type === 'binary') {
          console.log('Received Binary Message of ' + message.binaryData.length + ' bytes');
          connection.sendBytes(message.binaryData);
      }
  });

  // Callback when client closes the connection
  connection.on('close', function(reasonCode, description) {
      console.log((new Date()) + ' Peer ' + connection.remoteAddress + ' disconnected.');
  });
});
