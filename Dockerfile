FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app
COPY backend/pom.xml pom.xml
COPY backend/src src
RUN apk add --no-cache maven && mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/libtrack-*.jar libtrack.jar
EXPOSE 8000
ENTRYPOINT ["java", "-jar", "libtrack.jar"]
