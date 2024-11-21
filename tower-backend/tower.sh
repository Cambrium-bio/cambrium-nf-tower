# Launch backend server
exec java \
  -XX:+UnlockExperimentalVMOptions \
  -Dcom.sun.management.jmxremote \
  -noverify \
  -Dmicronaut.config.files=tower.yml \
  ${JAVA_OPTS} \
  -cp /app/resources:/app/classes:/app/libs/* \
  io.seqera.tower.Application
