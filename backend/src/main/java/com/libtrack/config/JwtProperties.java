package com.libtrack.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {

    private String secret = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET_KEY_AT_LEAST_256_BITS";
    private long expirationMs = 86400000L; // 24 hours

    public String getSecret() { return secret; }
    public void setSecret(String secret) { this.secret = secret; }

    public long getExpirationMs() { return expirationMs; }
    public void setExpirationMs(long expirationMs) { this.expirationMs = expirationMs; }
}
