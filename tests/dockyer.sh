docker rm -f caldor-fff && docker build -t caldor . && docker run --name=caldor-fff -dp 8001:8000 caldor

