package com.libtrack.dto.item;

public class BookCreateRequest extends ItemCreateRequest {
    private String genre;
    private String publisher;

    public String getGenre() { return genre; }
    public void setGenre(String genre) { this.genre = genre; }

    public String getPublisher() { return publisher; }
    public void setPublisher(String publisher) { this.publisher = publisher; }
}
