package org.hackaton.backend.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
        @NotBlank String fio,
        @NotBlank @Email String email,
        @NotBlank @Size(min = 8) String password
) {
}