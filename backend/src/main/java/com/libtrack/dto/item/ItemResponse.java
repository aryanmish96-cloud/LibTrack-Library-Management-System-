package com.libtrack.dto.item;

import com.libtrack.model.LibraryItem;

/**
 * Item response DTO — mirrors Python's ItemOut schema.
 * JSON field names use snake_case to match the frontend expectations.
 */
public class ItemResponse {

    private Long id;
    private String title;
    private String author;
    private String isbn;
    private int totalCopies;
    private int availableCopies;
    private String itemType;

    public static ItemResponse from(LibraryItem item) {
        ItemResponse r = new ItemResponse();
        r.id = item.getId();
        r.title = item.getTitle();
        r.author = item.getAuthor();
        r.isbn = item.getIsbn();
        r.totalCopies = item.getTotalCopies();
        r.availableCopies = item.getAvailableCopies();
        r.itemType = item.getItemType();
        return r;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getIsbn() { return isbn; }
    public int getTotalCopies() { return totalCopies; }
    public int getAvailableCopies() { return availableCopies; }
    public String getItemType() { return itemType; }
}
