package com.libtrack.dto.loan;

import com.libtrack.model.Loan;
import java.time.Instant;

/**
 * Loan response DTO — mirrors Python's LoanOut schema.
 * The frontend reads: id, item_id, member_id, checkout_date, due_date,
 * return_date, fine_amount, fine_paid, is_overdue, item_title.
 */
public class LoanResponse {

    private Long id;
    private Long itemId;
    private Long memberId;
    private Instant checkoutDate;
    private Instant dueDate;
    private Instant returnDate;
    private double fineAmount;
    private boolean finePaid;
    private boolean isOverdue;
    private String itemTitle;

    public static LoanResponse from(Loan loan) {
        LoanResponse r = new LoanResponse();
        r.id = loan.getId();
        r.itemId = loan.getItem() != null ? loan.getItem().getId() : null;
        r.memberId = loan.getMember() != null ? loan.getMember().getId() : null;
        r.checkoutDate = loan.getCheckoutDate();
        r.dueDate = loan.getDueDate();
        r.returnDate = loan.getReturnDate();
        r.fineAmount = loan.getFineAmount();
        r.finePaid = loan.isFinePaid();
        r.isOverdue = loan.isOverdue();
        r.itemTitle = loan.getItemTitle();
        return r;
    }

    public Long getId() { return id; }
    public Long getItemId() { return itemId; }
    public Long getMemberId() { return memberId; }
    public Instant getCheckoutDate() { return checkoutDate; }
    public Instant getDueDate() { return dueDate; }
    public Instant getReturnDate() { return returnDate; }
    public double getFineAmount() { return fineAmount; }
    public boolean isFinePaid() { return finePaid; }
    public boolean isIsOverdue() { return isOverdue; }
    public String getItemTitle() { return itemTitle; }
}
