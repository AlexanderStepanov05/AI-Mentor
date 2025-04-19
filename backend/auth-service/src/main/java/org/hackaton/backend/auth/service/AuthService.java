package org.hackaton.backend.auth.service;

import lombok.RequiredArgsConstructor;
import org.hackaton.backend.auth.dto.AuthResponse;
import org.hackaton.backend.auth.dto.LoginRequest;
import org.hackaton.backend.auth.dto.RegisterRequest;
import org.hackaton.backend.auth.entity.User;
import org.hackaton.backend.auth.exceptions.EmailAlreadyExistsException;
import org.hackaton.backend.auth.repository.UserRepository;
import org.hackaton.backend.auth.utils.JwtUtils;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new EmailAlreadyExistsException(request.email());
        }

        User user = User.builder()
                .email(request.email())
                .fio(request.fio())
                .password(passwordEncoder.encode(request.password()))
                .build();

        userRepository.save(user);

        return generateAuthResponse(user);
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.email())
                .orElseThrow(() -> new BadCredentialsException("Invalid credentials"));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new BadCredentialsException("Invalid credentials");
        }

        return generateAuthResponse(user);
    }

    private AuthResponse generateAuthResponse(User user) {
        String accessToken = jwtUtils.generateToken(user);
        return new AuthResponse(
                accessToken,
                null, // Можно добавить refresh токен
                Instant.now().plus(jwtUtils.getExpiration())
        );
    }
}
