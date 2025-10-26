# Porche_C2
    

docker build -t c2-server:latest .
docker build -t c2-client:latest .

docker network create c2-net

docker run -d --name c2-server --network c2-net -e SERVER_HOST=0.0.0.0 -e PORT=2222 c2-server
docker run -d --name c2-client --network c2-net c2-client