package com.libtrack.model;

import jakarta.persistence.*;

/**
 * Physical book — joined table "books" extending "items".
 * Maps to Python's Book subclass.
 */
@Entity
@Table(name = "books")
@DiscriminatorValue("book")
public class Book extends LibraryItem {

    private String genre;
    private String publisher;

    public String getGenre() { return genre; }
    public void setGenre(String genre) { this.genre = genre; }

    public String getPublisher() { return publisher; }
    public void setPublisher(String publisher) { this.publisher = publisher; }
}
