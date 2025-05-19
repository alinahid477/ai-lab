

# Start

Install via operator hub: 
-- Red Hat OpenShift Logging
-- Streams for Apache Kafka
-- Streams for Apache Kafka Console



## commands

oc extract -n kafka secret/logging-kafka-cluster-ca-cert --keys=ca.crt --to=- > ca.nogit.crt
keytool -keystore client.truststore.nogit.jks -alias CARoot -import -file ca.nogit.crt

## Important links

https://docs.redhat.com/fr/documentation/red_hat_streams_for_apache_kafka/2.7/html-single/getting_started_with_streams_for_apache_kafka_on_openshift/index#proc-using-amq-streams-str





#### Misc

oc run -n kafka kafka-consumer -ti --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server https://logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io --topic ocplogs-audit --from-beginning



oc run kafka-producer -n kafka -ti --image=registry.redhat.io/amq-streams/kafka-38-rhel9:2.8.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server logging-kafka-kafka-bootstrap:9092 --topic ocplogs-audit




kafka-console-consumer.sh \
--bootstrap-server logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io:443 \
--consumer-property security.protocol=SSL \
--consumer-property ssl.truststore.password=c97xOn13878b \
--consumer-property ssl.truststore.location=/home/anahid/ali/dev/repos/openshift-lab/baremetal/logging/kafka/kafka_2.13-3.9.0.redhat-00003/bin/client.truststore.nogit.jks \
--topic ocplogs-myapp --from-beginning



oc run -n kafka kafka-consumer -ti --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-consumer.sh \
--bootstrap-server logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io:443 \
--consumer-property security.protocol=SSL \
--consumer-property ssl.truststore.password=JbwIDgCf4X0I \
--consumer-property ssl.truststore.location=client.truststore.jks \
--topic ocplogs-audit --from-beginning


podman run -ti --rm -v ${PWD}/client.truststore.jks:/opt/kafka/config/client.truststore.jks:Z docker.io/apache/kafka:4.0.0-rc1 bin/kafka-console-consumer.sh   --bootstrap-server logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io:443 --consumer-property security.protocol=SSL --consumer-property ssl.truststore.password=JbwIDgCf4X0I --consumer-property ssl.truststore.location=/opt/kafka/config/client.truststore.jks --topic ocplogs-audit --from-beginning


kafka-console-consumer.sh   --bootstrap-server logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io:443 --consumer-property security.protocol=SSL --consumer-property ssl.truststore.password=JbwIDgCf4X0I --consumer-property ssl.truststore.location=/home/anahid/ali/dev/repos/openshift-lab/baremetal/logging/kafka/client.truststore.jks --topic ocplogs-audit --from-beginning


kafka-console-producer.sh \
--bootstrap-server logging-kafka-kafka-kafkaroute-bootstrap-kafka.apps.cluster-7msqx.dynamic.redhatworkshops.io:443 \
--producer-property security.protocol=SSL \
--producer-property ssl.truststore.password=JbwIDgCf4X0I \
--producer-property ssl.truststore.location=/home/anahid/ali/dev/repos/openshift-lab/baremetal/logging/kafka/client.truststore.jks \
--topic ocplogs-infrastructure





```

oc label namespace myapp pod-security.kubernetes.io/enforce=privileged --overwrite


oc run -n myapp kafka-cli \
  --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 \
  --restart=Never \
  --command -- \
  kafka-topics.sh \
    --bootstrap-server logging-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092 \
    --list

kubectl get pods -n myapp
kubectl logs kafka-cli -n myapp
kubectl delete pods kafka-cli -n myapp

# the below did not work
oc run -n myapp kafka-cli \
  --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 \
  --restart=Never \
  --command -- \
  bin/kafka-configs.sh --bootstrap-server logging-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092 \
  --entity-type topics --entity-name ocplogs-infrastructure \
  --alter --add-config retention.ms=1000

# this worked. it deleted the topic. I have no idea if freed diskspace or not.
oc run -n myapp kafka-cli \
  --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 \
  --restart=Never \
  --command -- \
  bin/kafka-topics.sh --bootstrap-server logging-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092 \
  --delete --topic ocplogs-infrastructure




kubectl logs kafka-cli -n myapp
kubectl delete pods kafka-cli -n myapp
```