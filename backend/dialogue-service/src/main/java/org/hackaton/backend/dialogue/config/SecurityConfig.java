package org.hackaton.backend.dialogue.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.oauth2.server.resource.authentication.ReactiveJwtAuthenticationConverterAdapter;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
@EnableWebFluxSecurity
public class SecurityConfig {

    @Bean
    public SecurityWebFilterChain securityFilterChain(
            ServerHttpSecurity http,
            JwtAuthConverter jwtAuthConverter
    ) {
        // Конвертер для реактивных приложений
        ReactiveJwtAuthenticationConverterAdapter converter =
                new ReactiveJwtAuthenticationConverterAdapter(jwtAuthConverter);

        return http
                .csrf(ServerHttpSecurity.CsrfSpec::disable)
                .authorizeExchange(ex -> ex
                        .pathMatchers("/api/dialogues/**").authenticated()
                        .anyExchange().permitAll()
                )
                .oauth2ResourceServer(o -> o
                        .jwt(j -> j.jwtAuthenticationConverter(converter))
                )
                .build();
    }
}
