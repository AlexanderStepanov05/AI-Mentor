package org.hackaton.backend.gateway.utils;

<<<<<<< HEAD
=======
import io.jsonwebtoken.Claims;
>>>>>>> frontend
import io.jsonwebtoken.Jwts;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

<<<<<<< HEAD
import java.time.Duration;

@Component
public class JwtUtils {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private Duration expiration;
=======
@Component
public class JwtUtils {

    private final String jwtSecret;

    public JwtUtils(@Value("${jwt.secret}") String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }
>>>>>>> frontend

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
<<<<<<< HEAD
                    .setSigningKey(secret)
=======
                    .setSigningKey(jwtSecret)
>>>>>>> frontend
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

<<<<<<< HEAD
    public String getUsernameFromToken(String token) {
        return Jwts.parser()
                .setSigningKey(secret)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
=======
    public String extractUserId(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(jwtSecret)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
>>>>>>> frontend
    }
}
