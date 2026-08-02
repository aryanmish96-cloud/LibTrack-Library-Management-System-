package com.libtrack.model;

/**
 * User roles — mirrors Python's Role enum (admin / member).
 */
public enum Role {
    ADMIN,
    MEMBER;

    /** Returns the lowercase string value stored in the DB and sent in JWT claims. */
    public String value() {
        return name().toLowerCase();
    }

    public static Role fromValue(String val) {
        return valueOf(val.toUpperCase());
    }
}
