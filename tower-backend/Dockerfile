# Use Java 11 base image
FROM openjdk:11-jdk-slim

# Install necessary packages
RUN apt-get update &&  apt-get upgrade -y && apt-get install -y bash wget

# Set working directory
#WORKDIR /app

# Copy the backend JAR file
COPY build/libs/tower-backend-*.jar /tower/tower-backend-all.jar

# Copy the startup script
COPY tower.sh /usr/local/bin/tower.sh

# Install jvmtop
RUN wget https://github.com/patric-r/jvmtop/releases/download/0.8.0/jvmtop-0.8.0.tar.gz -O- | tar xz \
    && chmod +x jvmtop.sh \
    && mv jvmtop.sh /usr/local/bin/jvmtop

# Expose the application port
EXPOSE 8080

# Set entrypoint script
CMD ["bash", "/usr/local/bin/tower.sh"]

