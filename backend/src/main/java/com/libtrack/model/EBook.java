package com.libtrack.model;

import jakarta.persistence.*;

/**
 * Digital book (EBook) — joined table "ebooks" extending "items".
 * Maps to Python's EBook subclass.
 */
@Entity
@Table(name = "ebooks")
@DiscriminatorValue("ebook")
public class EBook extends LibraryItem {

    @Column(name = "file_format")
    private String fileFormat = "PDF";

    @Column(name = "download_url")
    private String downloadUrl;

    public String getFileFormat() { return fileFormat; }
    public void setFileFormat(String fileFormat) { this.fileFormat = fileFormat; }

    public String getDownloadUrl() { return downloadUrl; }
    public void setDownloadUrl(String downloadUrl) { this.downloadUrl = downloadUrl; }
}
