FROM gradle:8.4-jdk17 AS build
WORKDIR /app

COPY build.gradle.kts settings.gradle.kts ./
COPY src ./src

RUN gradle clean build -x test --no-daemon

FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app

COPY --from=build /app/build/libs/*.jar ./app.jar

EXPOSE 8080
CMD ["java", "-jar", "app.jar"]