kubectl create namespace intellilogs

kubectl create secret docker-registry myquaycred \
  --docker-server=quay.io \
  --docker-username=rh-xxxxxxx \
  --docker-password=xxxxxxxxx \
  --namespace=intellilogs