package org.hackaton.backend.dialogue;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@SpringBootApplication(exclude = {
		SecurityAutoConfiguration.class
})
public class DialogueServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(DialogueServiceApplication.class, args);
	}

}
