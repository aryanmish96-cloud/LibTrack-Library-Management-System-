package com.libtrack.service;

import com.libtrack.model.*;
import com.libtrack.repository.ItemRepository;
import com.libtrack.repository.LoanRepository;
import com.libtrack.repository.ReservationRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;

/**
 * Loan service — mirrors Python's LoanService.
 * Handles checkout (with duplicate-loan and availability checks),
 * return (with fine calculation and reservation promotion).
 */
@Service
public class LoanService {

    private final LoanRepository loanRepo;
    private final ItemRepository itemRepo;
    private final ReservationRepository reservationRepo;

    @Value("${loan.period-days:14}")
    private int loanPeriodDays;

    @Value("${loan.fine-per-day:0.50}")
    private double finePerDay;

    public LoanService(LoanRepository loanRepo, ItemRepository itemRepo, ReservationRepository reservationRepo) {
        this.loanRepo = loanRepo;
        this.itemRepo = itemRepo;
        this.reservationRepo = reservationRepo;
    }

    @Transactional
    public Loan checkout(Long itemId, Long memberId) {
        LibraryItem item = itemRepo.findById(itemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Item not found"));

        if (!item.isAvailable()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "No copies currently available");
        }

        // Prevent double-checkout
        loanRepo.findActiveByItemAndMember(itemId, memberId).ifPresent(existing -> {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "You already have an active loan for this item");
        });

        // Fulfill any active reservation for this member+item
        reservationRepo.findActiveByItemAndMember(itemId, memberId).ifPresent(res -> {
            res.setStatus(ReservationStatus.FULFILLED);
            reservationRepo.save(res);
        });

        item.checkout();
        itemRepo.save(item);

        Loan loan = new Loan();
        loan.setItem(item);
        loan.setMember(memberRef(memberId));
        loan.setDueDate(Instant.now().plus(loanPeriodDays, ChronoUnit.DAYS));
        return loanRepo.save(loan);
    }

    @Transactional
    public Loan returnItem(Long loanId) {
        Loan loan = loanRepo.findById(loanId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Loan not found"));

        if (loan.getReturnDate() != null) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Item already returned");
        }

        loan.setReturnDate(Instant.now());
        loan.setFineAmount(loan.calculateFine(finePerDay));

        LibraryItem item = loan.getItem();
        item.returnItem();
        itemRepo.save(item);

        Loan saved = loanRepo.save(loan);

        // Promote the next waiting reservation to READY
        promoteNextReservation(item.getId());

        return saved;
    }

    public List<Loan> memberLoans(Long memberId) {
        return loanRepo.findByMemberIdOrderByCheckoutDateDesc(memberId);
    }

    public List<Loan> overdueLoans() {
        return loanRepo.findOverdue(Instant.now());
    }

    /** Creates a lightweight proxy Member so we don't need to load the full entity. */
    private Member memberRef(Long memberId) {
        Member m = new Member();
        m.setId(memberId);
        return m;
    }

    private void promoteNextReservation(Long itemId) {
        List<Reservation> waiting = reservationRepo.findByItemIdAndStatusOrderByPosition(itemId, ReservationStatus.WAITING);
        if (!waiting.isEmpty()) {
            Reservation next = waiting.get(0);
            next.setStatus(ReservationStatus.READY);
            reservationRepo.save(next);
        }
    }
}
