# Run client
`python runclient.py`
<br>
Client listens to localhost:30000 and uses certs from cert directory
# Run server
`python runserver.py`
<br>
Server starts on localhost:30000, uses certs from cert directory
 and writes logs to logs.txt file
 ## General info
 Server can handle as many clients as needed and is sustainable 
 to client disconnection and reconnection problems
 <br><br>
 'Restart' button can be pressed after the opponent disconnects
  or the game finishes
  <br><br>
  Client-server communication made using TLS on top of TCP