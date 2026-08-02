package com.libtrack.security;

import com.libtrack.model.Member;
import com.libtrack.repository.MemberRepository;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * Provides Spring Security's UserDetailsService so that the auto-configuration
 * does not generate a random password on startup.
 * We use JWTs so this is mainly needed to satisfy the auto-config bean requirement.
 */
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    private final MemberRepository memberRepo;

    public UserDetailsServiceImpl(MemberRepository memberRepo) {
        this.memberRepo = memberRepo;
    }

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Member member = memberRepo.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Member not found: " + email));
        return new org.springframework.security.core.userdetails.User(
                String.valueOf(member.getId()),
                member.getHashedPassword(),
                List.of(new SimpleGrantedAuthority("ROLE_" + member.getRole().name()))
        );
    }
}
