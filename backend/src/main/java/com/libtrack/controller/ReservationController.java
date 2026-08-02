package com.libtrack.controller;

import com.libtrack.dto.reservation.ReservationResponse;
import com.libtrack.service.ReservationService;
import org.springframework.http.HttpStatus;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Reservations controller — mirrors Python's reservations endpoints.
 * All endpoints require authentication.
 */
@RestController
@RequestMapping("/api/v1/reservations")
public class ReservationController {

    private final ReservationService reservationService;

    public ReservationController(ReservationService reservationService) {
        this.reservationService = reservationService;
    }

    /** GET /api/v1/reservations/my */
    @GetMapping("/my")
    public List<ReservationResponse> myReservations(Authentication auth) {
        Long memberId = getMemberId(auth);
        return reservationService.memberReservations(memberId).stream()
                .map(ReservationResponse::from).toList();
    }

    /** POST /api/v1/reservations/{item_id} */
    @PostMapping("/{itemId}")
    @ResponseStatus(HttpStatus.CREATED)
    public ReservationResponse reserve(@PathVariable Long itemId, Authentication auth) {
        Long memberId = getMemberId(auth);
        return ReservationResponse.from(reservationService.reserve(itemId, memberId));
    }

    /** POST /api/v1/reservations/{reservation_id}/cancel */
    @PostMapping("/{reservationId}/cancel")
    public ReservationResponse cancel(@PathVariable Long reservationId, Authentication auth) {
        getMemberId(auth); // ensure authenticated
        return ReservationResponse.from(reservationService.cancel(reservationId));
    }

    private Long getMemberId(Authentication auth) {
        if (auth == null) throw new AccessDeniedException("Authentication required");
        return Long.parseLong(auth.getName());
    }
}
