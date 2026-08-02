package com.libtrack.service;

import com.libtrack.model.*;
import com.libtrack.repository.ItemRepository;
import com.libtrack.repository.ReservationRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

/**
 * Reservation service — mirrors Python's ReservationService.
 * Handles reserve (with queue positioning), cancel, and member reservation listing.
 */
@Service
public class ReservationService {

    private final ReservationRepository reservationRepo;
    private final ItemRepository itemRepo;

    public ReservationService(ReservationRepository reservationRepo, ItemRepository itemRepo) {
        this.reservationRepo = reservationRepo;
        this.itemRepo = itemRepo;
    }

    @Transactional
    public Reservation reserve(Long itemId, Long memberId) {
        LibraryItem item = itemRepo.findById(itemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Item not found"));

        long currentQueue = reservationRepo.countByItemIdAndStatus(itemId, ReservationStatus.WAITING);

        Reservation reservation = new Reservation();
        reservation.setItem(item);
        reservation.setMember(memberRef(memberId));
        reservation.setQueuePosition((int) currentQueue + 1);
        return reservationRepo.save(reservation);
    }

    @Transactional
    public Reservation cancel(Long reservationId) {
        Reservation reservation = reservationRepo.findById(reservationId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Reservation not found"));
        reservation.setStatus(ReservationStatus.CANCELLED);
        return reservationRepo.save(reservation);
    }

    public List<Reservation> memberReservations(Long memberId) {
        return reservationRepo.findByMemberIdOrderByReservationDateDesc(memberId);
    }

    private Member memberRef(Long memberId) {
        Member m = new Member();
        m.setId(memberId);
        return m;
    }
}
