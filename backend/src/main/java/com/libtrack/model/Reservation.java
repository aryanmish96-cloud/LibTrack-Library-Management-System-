package com.libtrack.model;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * A reservation record for a member wanting a checked-out item.
 * Maps to the "reservations" table — mirrors Python's Reservation model.
 */
@Entity
@Table(name = "reservations")
public class Reservation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_id", nullable = false)
    private LibraryItem item;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @Column(name = "reservation_date", nullable = false)
    private Instant reservationDate = Instant.now();

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ReservationStatus status = ReservationStatus.WAITING;

    @Column(name = "queue_position", nullable = false)
    private int queuePosition;

    // ---- Business methods ----

    public String getItemTitle() {
        return item != null ? item.getTitle() : "";
    }

    // ---- Getters & Setters ----

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public LibraryItem getItem() { return item; }
    public void setItem(LibraryItem item) { this.item = item; }

    public Member getMember() { return member; }
    public void setMember(Member member) { this.member = member; }

    public Instant getReservationDate() { return reservationDate; }
    public void setReservationDate(Instant reservationDate) { this.reservationDate = reservationDate; }

    public ReservationStatus getStatus() { return status; }
    public void setStatus(ReservationStatus status) { this.status = status; }

    public int getQueuePosition() { return queuePosition; }
    public void setQueuePosition(int queuePosition) { this.queuePosition = queuePosition; }
}
