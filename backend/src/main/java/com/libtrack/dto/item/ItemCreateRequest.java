package com.libtrack.dto.item;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

/** Base fields shared by all item create requests. */
public abstract class ItemCreateRequest {

    @NotBlank
    private String title;

    @NotBlank
    private String author;

    private String isbn;

    @Min(1)
    private int totalCopies = 1;

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }

    public int getTotalCopies() { return totalCopies; }
    public void setTotalCopies(int totalCopies) { this.totalCopies = totalCopies; }
}
