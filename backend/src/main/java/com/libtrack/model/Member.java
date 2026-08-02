package com.libtrack.model;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.List;

/**
 * Represents a library member (user).
 * Maps to the "members" table — mirrors the Python Member model.
 */
@Entity
@Table(name = "members")
public class Member {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(name = "hashed_password", nullable = false)
    private String hashedPassword;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role = Role.MEMBER;

    @Column(name = "membership_date", nullable = false)
    private Instant membershipDate = Instant.now();

    @OneToMany(mappedBy = "member")
    private List<Loan> loans;

    @OneToMany(mappedBy = "member")
    private List<Reservation> reservations;

    // ---- Getters & Setters ----

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getHashedPassword() { return hashedPassword; }
    public void setHashedPassword(String hashedPassword) { this.hashedPassword = hashedPassword; }

    public Role getRole() { return role; }
    public void setRole(Role role) { this.role = role; }

    public Instant getMembershipDate() { return membershipDate; }
    public void setMembershipDate(Instant membershipDate) { this.membershipDate = membershipDate; }

    public List<Loan> getLoans() { return loans; }
    public List<Reservation> getReservations() { return reservations; }
}
