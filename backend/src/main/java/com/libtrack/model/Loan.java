package com.libtrack.model;

import jakarta.persistence.*;
import org.springframework.beans.factory.annotation.Value;

import java.time.Instant;

/**
 * A loan record representing a checkout of a library item by a member.
 * Maps to the "loans" table — mirrors Python's Loan SQLAlchemy model.
 */
@Entity
@Table(name = "loans")
public class Loan {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "item_id", nullable = false)
    private LibraryItem item;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @Column(name = "checkout_date", nullable = false)
    private Instant checkoutDate = Instant.now();

    @Column(name = "due_date", nullable = false)
    private Instant dueDate;

    @Column(name = "return_date")
    private Instant returnDate;

    @Column(name = "fine_amount")
    private double fineAmount = 0.0;

    @Column(name = "fine_paid")
    private boolean finePaid = false;

    // ---- Business methods ----

    /**
     * Calculates overdue fine based on configured rate.
     * finePerDay is passed in by the service (mirrors Python's settings.FINE_PER_DAY).
     */
    public double calculateFine(double finePerDay) {
        Instant end = returnDate != null ? returnDate : Instant.now();
        if (end.isAfter(dueDate)) {
            long overdueDays = (end.getEpochSecond() - dueDate.getEpochSecond()) / 86400;
            return Math.round(overdueDays * finePerDay * 100.0) / 100.0;
        }
        return 0.0;
    }

    public boolean isOverdue() {
        Instant end = returnDate != null ? returnDate : Instant.now();
        return end.isAfter(dueDate);
    }

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

    public Instant getCheckoutDate() { return checkoutDate; }
    public void setCheckoutDate(Instant checkoutDate) { this.checkoutDate = checkoutDate; }

    public Instant getDueDate() { return dueDate; }
    public void setDueDate(Instant dueDate) { this.dueDate = dueDate; }

    public Instant getReturnDate() { return returnDate; }
    public void setReturnDate(Instant returnDate) { this.returnDate = returnDate; }

    public double getFineAmount() { return fineAmount; }
    public void setFineAmount(double fineAmount) { this.fineAmount = fineAmount; }

    public boolean isFinePaid() { return finePaid; }
    public void setFinePaid(boolean finePaid) { this.finePaid = finePaid; }
}
