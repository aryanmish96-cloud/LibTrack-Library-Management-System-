package com.libtrack.controller;

import com.libtrack.dto.item.*;
import com.libtrack.model.Role;
import com.libtrack.service.CatalogService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Items (catalog) controller — mirrors Python's items endpoints.
 * Admin-only endpoints (add book/ebook/journal) check role via Authentication.
 * Public GET endpoints do not require authentication.
 */
@RestController
@RequestMapping("/api/v1/items")
public class ItemController {

    private final CatalogService catalogService;

    public ItemController(CatalogService catalogService) {
        this.catalogService = catalogService;
    }

    /** POST /api/v1/items/books — Admin only */
    @PostMapping("/books")
    @ResponseStatus(HttpStatus.CREATED)
    public ItemResponse addBook(@Valid @RequestBody BookCreateRequest req, Authentication auth) {
        requireAdmin(auth);
        return ItemResponse.from(catalogService.addBook(req));
    }

    /** POST /api/v1/items/ebooks — Admin only */
    @PostMapping("/ebooks")
    @ResponseStatus(HttpStatus.CREATED)
    public ItemResponse addEBook(@Valid @RequestBody EBookCreateRequest req, Authentication auth) {
        requireAdmin(auth);
        return ItemResponse.from(catalogService.addEBook(req));
    }

    /** POST /api/v1/items/journals — Admin only */
    @PostMapping("/journals")
    @ResponseStatus(HttpStatus.CREATED)
    public ItemResponse addJournal(@Valid @RequestBody JournalCreateRequest req, Authentication auth) {
        requireAdmin(auth);
        return ItemResponse.from(catalogService.addJournal(req));
    }

    /** GET /api/v1/items/search?title=&exact= */
    @GetMapping("/search")
    public List<ItemResponse> search(
            @RequestParam(required = false) String title,
            @RequestParam(defaultValue = "false") boolean exact) {
        return catalogService.search(title, exact).stream().map(ItemResponse::from).toList();
    }

    /** GET /api/v1/items/alphabetical */
    @GetMapping("/alphabetical")
    public List<ItemResponse> alphabetical() {
        return catalogService.alphabeticalCatalog().stream().map(ItemResponse::from).toList();
    }

    /** GET /api/v1/items/range?start=&end= */
    @GetMapping("/range")
    public List<ItemResponse> range(@RequestParam String start, @RequestParam String end) {
        return catalogService.titleRange(start, end).stream().map(ItemResponse::from).toList();
    }

    /** GET /api/v1/items/{id} */
    @GetMapping("/{id}")
    public ItemResponse getItem(@PathVariable Long id) {
        return ItemResponse.from(catalogService.getItem(id));
    }

    private void requireAdmin(Authentication auth) {
        if (auth == null) throw new AccessDeniedException("Authentication required");
        boolean isAdmin = auth.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .anyMatch(a -> a.equals("ROLE_ADMIN"));
        if (!isAdmin) throw new AccessDeniedException("Admin privileges required");
    }
}
