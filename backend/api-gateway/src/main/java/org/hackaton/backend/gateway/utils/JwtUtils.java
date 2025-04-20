package org.hackaton.backend.gateway.utils;

<<<<<<< HEAD
<<<<<<< HEAD
=======
import io.jsonwebtoken.Claims;
>>>>>>> frontend
=======
import io.jsonwebtoken.Claims;
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
import io.jsonwebtoken.Jwts;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

<<<<<<< HEAD
<<<<<<< HEAD
import java.time.Duration;

=======
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
@Component
public class JwtUtils {

    private final String jwtSecret;

<<<<<<< HEAD
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
=======
    public JwtUtils(@Value("${jwt.secret}") String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
<<<<<<< HEAD
<<<<<<< HEAD
                    .setSigningKey(secret)
=======
                    .setSigningKey(jwtSecret)
>>>>>>> frontend
=======
                    .setSigningKey(jwtSecret)
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

<<<<<<< HEAD
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
=======
    public String extractUserId(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(jwtSecret)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.getSubject();
>>>>>>> a3869b092b31b7e8dc8ffb2474589b1d101be40d
    }
}
