package com.libtrack.dto.auth;

/** Token response — mirrors Python's Token schema: { access_token, token_type }. */
public class TokenResponse {

    private String accessToken;
    private String tokenType = "bearer";

    public TokenResponse(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getAccessToken() { return accessToken; }
    public String getTokenType() { return tokenType; }
}
