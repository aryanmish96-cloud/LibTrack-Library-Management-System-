package com.libtrack.model;

/**
 * Reservation status — mirrors Python's ReservationStatus enum.
 */
public enum ReservationStatus {
    WAITING,
    READY,
    FULFILLED,
    CANCELLED;

    public String value() {
        return name().toLowerCase();
    }
}
