package org.hackaton.backend.dialogue.repository;

import org.hackaton.backend.dialogue.entity.Dialogue;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import reactor.core.publisher.Flux;

import java.util.UUID;

public interface DialogueRepository extends ReactiveMongoRepository<Dialogue, String> {
    Flux<Dialogue> findAllByUserId(UUID userId);
}
