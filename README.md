# C2 Project

This project implements a **simple Command-and-Control (C2)** pair:

-  **`server.py`** — multi-session server with interactive session switching.
-  **`client.py`** — persistent client that executes received commands and returns stdout/stderr.

All communication is protected with **TLS encryption** and optionally with **HMAC authentication** for message integrity.

## Manual Setup
### Requirements:
- `Python 3.7+`

For manual setup, clone this repository and from one terminal start the server:
```
cd server
python server.py
```
Then on a different terminal (one or more) open the clients with:
```
cd client
python client.py 127.0.0.1 2222
```
For adding more clients, just open more terminals and run the command above.
## Containerized setup
### Requirements:
- `Docker` or `Podman`

Pull the images with:
```
docker pull itamarsh/c2-client:latest
docker pull itamarsh/c2-server:latest
```
(You can also build the images manually, instructions below.)`
Open docker netwrok with:
```
docker network create c2-net
```
Then from one terminal, open the server with:
```
docker run -it --rm --name c2-server --network c2-net docker.io/itamarsh/c2-server
```
You can add those flags:
-  `-e SERVER_HOST=<ip>` — for changing the server host.
-  `-e PORT=<port>` — for changing the port (It wont be exposed tho).
-  `-e HMAC=<hmac_key>` — for changing the HMAC key.

And from a second terminal you can add as many clients as you want with:
```
docker run -d --rm --network c2-net docker.io/itamarsh/c2-client
```
You can add those flags:
-  `-e CLIENT_HOST=<ip>` — for changing the client host.
-  `-e HMAC=<hmac_key>` — for changing the HMAC key.
And if you want to edit the server name and port, you can add at the end:
```
python client.py <server_hostname> <port>
```

# Usage
After the client is connected to the server, you can send commands from the server to the client.
There are 3 special commands:
-  **`stop`** — Stop the current session.
-  **`sessions`** — Show the connected sessions.
-  **`use <id>`** — Take session ID as argument, and switch to this sessions.

# Protocol

### Establishing connection

-   The **server** listens on a fixed **TCP port (2222)**.
-   The socket is wrapped with **TLS**, using:
    -   A **public certificate** → `cert.pem`
    -   A **private key** → `key.pem`   
-   When a **client** connects, it sends its **hostname** to register itself.
-   The **server** stores this connection inside a `Session` object containing:
    -   A unique **session ID**
    -   The **client’s hostname**
    -   The **socket connection**
----------
### Messaging Flow

1.  **Message Input (Server → Client)**  
    The user types a command in the server's terminal.  
    The server:
    -   Signs the command using the shared **HMAC key**        
    -   Sends **both the command and its signature** to the client
2.  **Verification & Execution (Client Side)**
    -   The client verifies the **HMAC signature** to ensure authenticity.
    -   If the signature is valid, the client executes the command.
    -   The **stdout** and **stderr** outputs are combined into a single message.
3.  **Response (Client → Server)**
    -   The client signs the output with the **same HMAC key**.
    -   It sends both the **output** and its **signature** back to the server.
4.  **Output Display (Server Side)**
    -   The server verifies the signature.
    -   If valid, the output is printed to the console.
    -   The server then waits for the next input.

# Logging
The server logs are printed to the screen, and saved to a file called `server.log` in the server's home directory.
The logs are in the following format:
```
[Date]  [Time] - [Client Hostname] [Client Session ID] - [Message]
```
* For server logs, The `[Client Hostname]` field is set to the server's hostname, and the `[Client Session ID]` field is set to the word server.

If you want to see the logs insinde a container, run:
```
docker exec c2-server cat server.log
```

## Building the images:
If you want to build the images manually, clone this repository and build the server image with:
```
cd server
docker build -t docker.io/itamarsh/c2-server:latest .
```
Build the client image with:
```
cd client
docker build -t docker.io/itamarsh/c2-client:latest .
```
