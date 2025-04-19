package org.hackaton.backend.dialogue.service;

import lombok.RequiredArgsConstructor;
import org.hackaton.backend.dialogue.entity.Dialogue;
import org.hackaton.backend.dialogue.entity.Message;
import org.hackaton.backend.dialogue.repository.DialogueRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.ArrayList;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class DialogueService {
    private final DialogueRepository repository;

    public Mono<Dialogue> createDialogue(UUID userId) {
        return repository.save(
                Dialogue.builder()
                        .userId(userId)
                        .messages(new ArrayList<>())
                        .createdAt(Instant.now())
                        .modelVersion("v1.0")
                        .build()
        );
    }

    public Mono<Dialogue> addMessage(String dialogueId, Message message) {
        return repository.findById(dialogueId)
                .flatMap(dialogue -> {
                    dialogue.getMessages().add(message);
                    return repository.save(dialogue);
                });
    }
}
