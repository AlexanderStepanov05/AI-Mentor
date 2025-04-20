package org.hackaton.backend.auth.dto;

import java.time.Instant;

public record AuthResponse(
        String accessToken,
        String refreshToken,
        Instant expiresAt
) {}
