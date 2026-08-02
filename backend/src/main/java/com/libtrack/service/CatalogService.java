package com.libtrack.service;

import com.libtrack.dto.item.*;
import com.libtrack.model.*;
import com.libtrack.repository.ItemRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

/**
 * Catalog service — mirrors Python's CatalogService.
 * Delegates to ItemRepository for all CRUD and search operations.
 * Note: BST search from the Python version is replaced here with equivalent
 * JPQL database queries which achieve the same functionality.
 */
@Service
public class CatalogService {

    private final ItemRepository itemRepo;

    public CatalogService(ItemRepository itemRepo) {
        this.itemRepo = itemRepo;
    }

    public Book addBook(BookCreateRequest req) {
        Book book = new Book();
        book.setTitle(req.getTitle());
        book.setAuthor(req.getAuthor());
        book.setIsbn(req.getIsbn());
        book.setTotalCopies(req.getTotalCopies());
        book.setAvailableCopies(req.getTotalCopies());
        book.setGenre(req.getGenre());
        book.setPublisher(req.getPublisher());
        return (Book) itemRepo.save(book);
    }

    public EBook addEBook(EBookCreateRequest req) {
        EBook ebook = new EBook();
        ebook.setTitle(req.getTitle());
        ebook.setAuthor(req.getAuthor());
        ebook.setIsbn(req.getIsbn());
        ebook.setTotalCopies(req.getTotalCopies());
        ebook.setAvailableCopies(req.getTotalCopies());
        ebook.setFileFormat(req.getFileFormat() != null ? req.getFileFormat() : "PDF");
        ebook.setDownloadUrl(req.getDownloadUrl());
        return (EBook) itemRepo.save(ebook);
    }

    public Journal addJournal(JournalCreateRequest req) {
        Journal journal = new Journal();
        journal.setTitle(req.getTitle());
        journal.setAuthor(req.getAuthor());
        journal.setIsbn(req.getIsbn());
        journal.setTotalCopies(req.getTotalCopies());
        journal.setAvailableCopies(req.getTotalCopies());
        journal.setIssueNumber(req.getIssueNumber());
        journal.setVolume(req.getVolume());
        return (Journal) itemRepo.save(journal);
    }

    public LibraryItem getItem(Long id) {
        return itemRepo.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Item not found"));
    }

    public List<LibraryItem> search(String title, boolean exact) {
        if (title == null || title.isBlank()) {
            return itemRepo.findAll();
        }
        if (exact) {
            return itemRepo.findByTitleExact(title);
        }
        return itemRepo.searchByTitleContaining(title);
    }

    public List<LibraryItem> alphabeticalCatalog() {
        return itemRepo.findAllAlphabetical();
    }

    public List<LibraryItem> titleRange(String start, String end) {
        return itemRepo.findByTitleRange(start, end);
    }
}
