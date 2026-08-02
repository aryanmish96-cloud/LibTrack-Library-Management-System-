package com.libtrack.controller;

import com.libtrack.dto.loan.LoanResponse;
import com.libtrack.service.LoanService;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Loans controller — mirrors Python's loans endpoints.
 * All endpoints require authentication. /overdue requires admin.
 */
@RestController
@RequestMapping("/api/v1/loans")
public class LoanController {

    private final LoanService loanService;

    public LoanController(LoanService loanService) {
        this.loanService = loanService;
    }

    /** POST /api/v1/loans/checkout/{item_id} — authenticated member */
    @PostMapping("/checkout/{itemId}")
    @ResponseStatus(HttpStatus.CREATED)
    public LoanResponse checkout(@PathVariable Long itemId, Authentication auth) {
        Long memberId = getMemberId(auth);
        return LoanResponse.from(loanService.checkout(itemId, memberId));
    }

    /** POST /api/v1/loans/{loan_id}/return — authenticated member */
    @PostMapping("/{loanId}/return")
    public LoanResponse returnItem(@PathVariable Long loanId, Authentication auth) {
        getMemberId(auth); // ensure authenticated
        return LoanResponse.from(loanService.returnItem(loanId));
    }

    /** GET /api/v1/loans/my — authenticated member's loans */
    @GetMapping("/my")
    public List<LoanResponse> myLoans(Authentication auth) {
        Long memberId = getMemberId(auth);
        return loanService.memberLoans(memberId).stream().map(LoanResponse::from).toList();
    }

    /** GET /api/v1/loans/overdue — admin only */
    @GetMapping("/overdue")
    public List<LoanResponse> overdueLoans(Authentication auth) {
        requireAdmin(auth);
        return loanService.overdueLoans().stream().map(LoanResponse::from).toList();
    }

    private Long getMemberId(Authentication auth) {
        if (auth == null) throw new AccessDeniedException("Authentication required");
        return Long.parseLong(auth.getName());
    }

    private void requireAdmin(Authentication auth) {
        if (auth == null) throw new AccessDeniedException("Authentication required");
        boolean isAdmin = auth.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .anyMatch(a -> a.equals("ROLE_ADMIN"));
        if (!isAdmin) throw new AccessDeniedException("Admin privileges required");
    }
}
