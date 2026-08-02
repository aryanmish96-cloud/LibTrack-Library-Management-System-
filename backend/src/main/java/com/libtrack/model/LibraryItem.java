package com.libtrack.model;

import jakarta.persistence.*;
import java.util.List;

/**
 * Base entity for all catalog items.
 * Uses JPA JOINED inheritance — matches Python's SQLAlchemy joined-table polymorphism.
 * Subclasses: Book, EBook, Journal.
 */
@Entity
@Table(name = "items")
@Inheritance(strategy = InheritanceType.JOINED)
@DiscriminatorColumn(name = "item_type", discriminatorType = DiscriminatorType.STRING)
public abstract class LibraryItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String author;

    @Column(unique = true)
    private String isbn;

    @Column(name = "total_copies", nullable = false)
    private int totalCopies = 1;

    @Column(name = "available_copies", nullable = false)
    private int availableCopies = 1;

    // Exposed so DTOs can read the discriminator value (e.g. "book", "ebook", "journal")
    @Column(name = "item_type", insertable = false, updatable = false)
    private String itemType;

    @OneToMany(mappedBy = "item")
    private List<Loan> loans;

    @OneToMany(mappedBy = "item")
    private List<Reservation> reservations;

    // ---- Business methods ----

    public boolean isAvailable() {
        return availableCopies > 0;
    }

    public void checkout() {
        if (!isAvailable()) throw new IllegalStateException("No copies available for checkout");
        availableCopies--;
    }

    public void returnItem() {
        if (availableCopies >= totalCopies) throw new IllegalStateException("All copies already accounted for");
        availableCopies++;
    }

    // ---- Getters & Setters ----

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public int getTotalCopies() { return totalCopies; }
    public void setTotalCopies(int totalCopies) { this.totalCopies = totalCopies; }

    public int getAvailableCopies() { return availableCopies; }
    public void setAvailableCopies(int availableCopies) { this.availableCopies = availableCopies; }

    public String getItemType() { return itemType; }

    public List<Loan> getLoans() { return loans; }
    public List<Reservation> getReservations() { return reservations; }
}
