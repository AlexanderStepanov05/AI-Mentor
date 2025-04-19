package org.hackaton.backend.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator routes(
            RouteLocatorBuilder builder,
            JwtAuthFilter jwtAuthFilter
    ) {
        return builder.routes()
                .route("auth-service", r -> r
                        .path("/api/auth/**")
                        .filters(f -> f
                                .filter(jwtAuthFilter)
                                .rewritePath("/api/auth/(?<segment>.*)", "/${segment}")
                        )
                        .uri("lb://auth-service")
                )
                .route("dialogue-service", r -> r
                        .path("/api/dialogues/**")
                        .filters(f -> f
                                .filter(jwtAuthFilter)
                                .rewritePath("/api/dialogues/(?<segment>.*)", "/${segment}")
                        )
                        .uri("lb://dialogue-service")
                )
                .route("ml-service", r -> r
                        .path("/api/ml/**")
                        .filters(f -> f
                                .filter(jwtAuthFilter)
                                .rewritePath("/api/ml/(?<segment>.*)", "/${segment}")
                        )
                        .uri("lb://ml-service")
                )
                .build();
    }
}
