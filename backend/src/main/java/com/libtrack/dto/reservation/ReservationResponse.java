package com.libtrack.dto.reservation;

import com.libtrack.model.Reservation;
import java.time.Instant;

/**
 * Reservation response DTO — mirrors Python's ReservationOut schema.
 * The frontend reads: id, item_id, member_id, reservation_date, status,
 * queue_position, item_title.
 */
public class ReservationResponse {

    private Long id;
    private Long itemId;
    private Long memberId;
    private Instant reservationDate;
    private String status;
    private int queuePosition;
    private String itemTitle;

    public static ReservationResponse from(Reservation res) {
        ReservationResponse r = new ReservationResponse();
        r.id = res.getId();
        r.itemId = res.getItem() != null ? res.getItem().getId() : null;
        r.memberId = res.getMember() != null ? res.getMember().getId() : null;
        r.reservationDate = res.getReservationDate();
        r.status = res.getStatus().value();
        r.queuePosition = res.getQueuePosition();
        r.itemTitle = res.getItemTitle();
        return r;
    }

    public Long getId() { return id; }
    public Long getItemId() { return itemId; }
    public Long getMemberId() { return memberId; }
    public Instant getReservationDate() { return reservationDate; }
    public String getStatus() { return status; }
    public int getQueuePosition() { return queuePosition; }
    public String getItemTitle() { return itemTitle; }
}
