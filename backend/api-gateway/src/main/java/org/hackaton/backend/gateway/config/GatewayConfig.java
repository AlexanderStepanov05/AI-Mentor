package org.hackaton.backend.gateway.config;

<<<<<<< HEAD
<<<<<<< HEAD
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
=======
import org.hackaton.backend.gateway.utils.JwtUtils;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;
>>>>>>> frontend
=======
import org.hackaton.backend.gateway.utils.JwtUtils;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d

@Configuration
public class GatewayConfig {

    @Bean
<<<<<<< HEAD
<<<<<<< HEAD
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
=======
=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
    public CorsWebFilter corsFilter() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("http://localhost:5173");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return new CorsWebFilter(source);
<<<<<<< HEAD
>>>>>>> frontend
=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
    }
}
