package org.hackaton.backend.dialogue.controller;

import lombok.RequiredArgsConstructor;
import org.hackaton.backend.dialogue.dto.MessageRequest;
import org.hackaton.backend.dialogue.entity.Dialogue;
import org.hackaton.backend.dialogue.entity.Message;
import org.hackaton.backend.dialogue.service.DialogueService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.UUID;

@RestController
@RequestMapping("/api/dialogues")
@RequiredArgsConstructor
public class DialogueController {
    private final DialogueService service;

    @PostMapping
    public Mono<ResponseEntity<Dialogue>> createDialogue(
            @AuthenticationPrincipal Jwt jwt
    ) {
        UUID userId = UUID.fromString(jwt.getSubject());
        return service.createDialogue(userId)
                .map(ResponseEntity::ok);
    }

    @PostMapping("/{id}/messages")
    public Mono<ResponseEntity<Dialogue>> addMessage(
            @PathVariable String id,
            @RequestBody MessageRequest request,
            @AuthenticationPrincipal Jwt jwt
    ) {
        Message message = Message.builder()
                .content(request.content())
                .isUser(request.isUser())
                .timestamp(Instant.now())
                .build();

        return service.addMessage(id, message)
                .map(ResponseEntity::ok);
    }
}
