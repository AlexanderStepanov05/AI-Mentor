package org.hackaton.backend.dialogue.dto;


import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record MessageRequest(
        @NotBlank(message = "Content cannot be empty")
        String content,

        @NotNull(message = "isUser flag is required")
        Boolean isUser
) {}
