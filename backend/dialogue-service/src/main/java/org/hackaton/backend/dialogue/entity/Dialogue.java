package org.hackaton.backend.dialogue.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Document(collection = "dialogues")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Dialogue {
    @Id
    private String id;

    @Indexed
    private UUID userId;

    private List<Message> messages;
    private Instant createdAt;
    private String modelVersion;
}