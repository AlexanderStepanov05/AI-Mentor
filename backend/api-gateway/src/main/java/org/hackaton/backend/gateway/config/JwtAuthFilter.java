package org.hackaton.backend.gateway.config;

import org.hackaton.backend.gateway.utils.JwtUtils;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
<<<<<<< HEAD
<<<<<<< HEAD
import org.springframework.http.HttpStatus;
=======
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
>>>>>>> frontend
=======
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class JwtAuthFilter implements GatewayFilter {

    private final JwtUtils jwtUtils;

    public JwtAuthFilter(JwtUtils jwtUtils) {
        this.jwtUtils = jwtUtils;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
<<<<<<< HEAD
<<<<<<< HEAD
        String token = extractToken(exchange.getRequest());
        if (token == null || !jwtUtils.validateToken(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
=======
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().toString();

        if (isPublicEndpoint(path)) {
            return chain.filter(exchange);
        }
=======
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().toString();

        if (isPublicEndpoint(path)) {
            return chain.filter(exchange);
        }
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d

        String token = extractToken(request);
        if (token == null) {
            return unauthorized(exchange, "Missing JWT token");
        }

        if (!jwtUtils.validateToken(token)) {
            return unauthorized(exchange, "Invalid JWT token");
        }

        String userId = jwtUtils.extractUserId(token);
        ServerHttpRequest modifiedRequest = request.mutate()
                .header("X-User-Id", userId)
                .build();

        return chain.filter(exchange.mutate().request(modifiedRequest).build());
    }

    private boolean isPublicEndpoint(String path) {
        return path.startsWith("/api/auth/login")
                || path.startsWith("/api/auth/register")
                || path.startsWith("/actuator/health");
<<<<<<< HEAD
>>>>>>> frontend
=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
    }

    private String extractToken(ServerHttpRequest request) {
        String header = request.getHeaders().getFirst("Authorization");
<<<<<<< HEAD
<<<<<<< HEAD
        return header.startsWith("Bearer ")
                ? header.substring(7)
                : null;
=======
=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
        if (header.startsWith("Bearer ")) {
            return header.substring(7);
        }
        return null;
    }

    private Mono<Void> unauthorized(ServerWebExchange exchange, String message) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        String body = String.format("{\"error\": \"%s\"}", message);
        DataBuffer buffer = exchange.getResponse().bufferFactory().wrap(body.getBytes());
        return exchange.getResponse().writeWith(Mono.just(buffer));
<<<<<<< HEAD
>>>>>>> frontend
=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
    }
}
