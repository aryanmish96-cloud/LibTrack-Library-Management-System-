package com.libtrack.service;

import com.libtrack.dto.auth.LoginRequest;
import com.libtrack.dto.auth.RegisterRequest;
import com.libtrack.model.Member;
import com.libtrack.repository.MemberRepository;
import com.libtrack.security.JwtUtil;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * Authentication service — mirrors Python's AuthService.
 * Handles registration (with duplicate-email check) and login (with JWT issue).
 */
@Service
public class AuthService {

    private final MemberRepository memberRepo;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthService(MemberRepository memberRepo, PasswordEncoder passwordEncoder, JwtUtil jwtUtil) {
        this.memberRepo = memberRepo;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    public Member register(RegisterRequest req) {
        if (memberRepo.existsByEmail(req.getEmail())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Email already registered");
        }
        Member member = new Member();
        member.setName(req.getName());
        member.setEmail(req.getEmail());
        member.setHashedPassword(passwordEncoder.encode(req.getPassword()));
        return memberRepo.save(member);
    }

    public String login(LoginRequest req) {
        Member member = memberRepo.findByEmail(req.getEmail())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Incorrect email or password"));

        if (!passwordEncoder.matches(req.getPassword(), member.getHashedPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Incorrect email or password");
        }

        return jwtUtil.generateToken(String.valueOf(member.getId()), member.getRole().value());
    }
}
