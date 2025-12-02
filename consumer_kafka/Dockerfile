FROM farberg/apache-hadoop:3.4.1

USER root

# Cài packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install kafka-python hdfs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Tạo user
RUN groupadd -g 1001 hadoop 2>/dev/null || true && \
    useradd -u 1001 -g 1001 -m -s /bin/bash hadoop 2>/dev/null || true

# Tạo thư mục
RUN mkdir -p /opt/hadoop/logs \
             /hadoop/dfs/name \
             /hadoop/dfs/data \
             /tmp/hadoop-hadoop

# Config với bind 0.0.0.0
RUN cat > /opt/hadoop/etc/hadoop/core-site.xml <<'EOF'
<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://my-hadoop-hadoop-hdfs-nn:9000</value>
  </property>
</configuration>
EOF

RUN cat > /opt/hadoop/etc/hadoop/hdfs-site.xml <<'EOF'
<?xml version="1.0"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///hadoop/dfs/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///hadoop/dfs/data</value>
  </property>
  <property>
    <name>dfs.namenode.rpc-bind-host</name>
    <value>0.0.0.0</value>
  </property>
  <property>
    <name>dfs.namenode.http-bind-host</name>
    <value>0.0.0.0</value>
  </property>
</configuration>
EOF

# Copy code
COPY consumer-simple.py /opt/consumer.py

# Set ownership
RUN chown -R hadoop:hadoop /opt/hadoop /hadoop /tmp/hadoop-hadoop && \
    chmod -R 775 /opt/hadoop /hadoop /tmp/hadoop-hadoop

USER root
WORKDIR /opt/hadoop