package com.libtrack.dto.auth;

import com.libtrack.model.Member;
import java.time.Instant;

/** Response DTO for member registration — mirrors Python's MemberOut schema. */
public class MemberResponse {

    private Long id;
    private String name;
    private String email;
    private String role;
    private Instant membershipDate;

    public static MemberResponse from(Member m) {
        MemberResponse r = new MemberResponse();
        r.id = m.getId();
        r.name = m.getName();
        r.email = m.getEmail();
        r.role = m.getRole().value();
        r.membershipDate = m.getMembershipDate();
        return r;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getRole() { return role; }
    public Instant getMembershipDate() { return membershipDate; }
}
