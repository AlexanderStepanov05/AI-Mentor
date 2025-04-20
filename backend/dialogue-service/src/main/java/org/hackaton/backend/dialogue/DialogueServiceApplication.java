package org.hackaton.backend.dialogue;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
<<<<<<< HEAD
<<<<<<< HEAD

@SpringBootApplication
=======
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@SpringBootApplication(exclude = {
		SecurityAutoConfiguration.class
})
>>>>>>> frontend
=======
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@SpringBootApplication(exclude = {
		SecurityAutoConfiguration.class
})
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
public class DialogueServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(DialogueServiceApplication.class, args);
	}

}
