

```
kubectl create namespace intellilogs

kubectl create secret docker-registry myquaycred \
  --docker-server=quay.io \
  --docker-username=<your-username> \
  --docker-password=<your-password> \
  --docker-email=<your-email> \
  --namespace=intellilogs

kubectl apply -f intellilog-envvars.yaml

kubectl apply -f backend-aiapp-deployment.yaml
kubectl apply -f backend-wsserver-deployment.yaml
kubectl apply -f frontend-aiapp-deployment.yaml

```