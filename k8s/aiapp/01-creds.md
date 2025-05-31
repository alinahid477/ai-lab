kubectl create namespace intellilogs

kubectl create secret docker-registry myquaycred \
  --docker-server=quay.io \
  --docker-username=rh-xxxxxxx \
  --docker-password=xxxxxxxxx \
  --namespace=intellilogs

kubectl create ns ollama

kubectl create secret docker-registry myquaycred \
  --docker-server=quay.io \
  --docker-username=xxxxxx \
  --docker-password=xxxxxxx \
  --namespace=ollama