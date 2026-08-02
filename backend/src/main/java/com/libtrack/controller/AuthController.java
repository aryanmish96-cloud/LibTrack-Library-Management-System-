package com.libtrack.controller;

import com.libtrack.dto.auth.*;
import com.libtrack.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

/**
 * Auth controller — exposes /api/v1/auth/register and /api/v1/auth/login.
 * Mirrors Python's auth endpoints exactly.
 */
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /** POST /api/v1/auth/register — returns 201 with MemberResponse */
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public MemberResponse register(@Valid @RequestBody RegisterRequest req) {
        return MemberResponse.from(authService.register(req));
    }

    /** POST /api/v1/auth/login — returns 200 with { access_token, token_type } */
    @PostMapping("/login")
    public TokenResponse login(@Valid @RequestBody LoginRequest req) {
        String token = authService.login(req);
        return new TokenResponse(token);
    }
}
